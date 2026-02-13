"""Ticket CRUD API routes.

Queries join raw_tickets + processed_tickets to return a unified view.
Tag updates go to processed_tickets; status updates go to raw_tickets.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.ticket import ProcessedTicket, RawTicket
from app.schemas.ticket import (
    ProcessingStatus,
    TicketListResponse,
    TicketResponse,
    UpdateStatusRequest,
    UpdateTagsRequest,
)

logger = logging.getLogger("app.api.tickets")
router = APIRouter()


def _build_ticket_response(raw: RawTicket) -> TicketResponse:
    """Build a TicketResponse from a RawTicket with its eagerly-loaded processed_ticket."""
    processed = raw.processed_ticket
    return TicketResponse(
        id=raw.id,
        title=raw.title,
        content=raw.content,
        tags=processed.tags if processed else None,
        demographics=processed.demographics if processed else None,
        sentiment=processed.sentiment if processed else None,
        emotional_tone=processed.emotional_tone if processed else None,
        confidence=processed.confidence if processed else None,
        customer_email=raw.customer_email,
        status=raw.status,
        processing_status=(
            ProcessingStatus.COMPLETED if processed else ProcessingStatus.PENDING
        ),
        created_at=raw.created_at,
        last_updated=raw.last_updated,
    )


@router.get("/tickets", response_model=TicketListResponse)
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    """Return all tickets (raw + processed joined)."""
    logger.info("Fetching all tickets")
    result = await db.execute(
        select(RawTicket)
        .options(selectinload(RawTicket.processed_ticket))
        .order_by(RawTicket.created_at.desc())
    )
    raw_tickets = result.scalars().all()
    logger.info("Returning %d ticket(s)", len(raw_tickets))
    return TicketListResponse(
        tickets=[_build_ticket_response(rt) for rt in raw_tickets],
        count=len(raw_tickets),
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return a single ticket by raw ticket ID."""
    logger.info("Fetching ticket %s", ticket_id)
    result = await db.execute(
        select(RawTicket)
        .options(selectinload(RawTicket.processed_ticket))
        .where(RawTicket.id == ticket_id)
    )
    raw_ticket = result.scalar_one_or_none()
    if raw_ticket is None:
        logger.warning("Ticket %s not found", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")
    logger.debug("Ticket %s: title=%s, status=%s", ticket_id, raw_ticket.title, raw_ticket.status)
    return _build_ticket_response(raw_ticket)


@router.post("/tickets/{ticket_id}/tags", response_model=TicketResponse)
async def update_ticket_tags(
    ticket_id: uuid.UUID,
    body: UpdateTagsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manually update tags on a ticket (override LLM-generated tags).

    Tags are stored on the processed_tickets row. If no processed record exists
    yet (ticket still pending), one is created to hold the manual tags.
    """
    logger.info("Updating tags for ticket %s with %d tag(s)", ticket_id, len(body.tags))

    # Fetch the raw ticket with its processed record
    result = await db.execute(
        select(RawTicket)
        .options(selectinload(RawTicket.processed_ticket))
        .where(RawTicket.id == ticket_id)
    )
    raw_ticket = result.scalar_one_or_none()
    if raw_ticket is None:
        logger.warning("Ticket %s not found for tag update", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")

    processed = raw_ticket.processed_ticket
    new_tags = [tag.model_dump() for tag in body.tags]

    if processed:
        old_tags = processed.tags
        processed.tags = new_tags
        processed.last_updated = datetime.now(timezone.utc)
        logger.info("Tags updated on processed ticket: %s -> %s", old_tags, new_tags)
    else:
        # Create a minimal processed ticket to hold manual tags
        processed = ProcessedTicket(
            raw_ticket_id=ticket_id,
            tags=new_tags,
        )
        db.add(processed)
        logger.info("Created processed ticket for manual tags on raw ticket %s", ticket_id)

    await db.flush()
    return _build_ticket_response(raw_ticket)


@router.post("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: uuid.UUID,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update the status of a ticket (on the raw_tickets record)."""
    logger.info("Updating status for ticket %s to '%s'", ticket_id, body.status.value)

    result = await db.execute(
        select(RawTicket)
        .options(selectinload(RawTicket.processed_ticket))
        .where(RawTicket.id == ticket_id)
    )
    raw_ticket = result.scalar_one_or_none()
    if raw_ticket is None:
        logger.warning("Ticket %s not found for status update", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_status = raw_ticket.status
    raw_ticket.status = body.status.value
    raw_ticket.last_updated = datetime.now(timezone.utc)
    await db.flush()
    logger.info("Status updated for ticket %s: %s -> %s", ticket_id, old_status, raw_ticket.status)
    return _build_ticket_response(raw_ticket)
