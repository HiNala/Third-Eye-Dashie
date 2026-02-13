"""Ticket CRUD API routes."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import (
    TicketListResponse,
    TicketResponse,
    UpdateStatusRequest,
    UpdateTagsRequest,
)

logger = logging.getLogger("app.api.tickets")
router = APIRouter()


@router.get("/tickets", response_model=TicketListResponse)
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    """Return all tickets."""
    logger.info("Fetching all tickets")
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    tickets = result.scalars().all()
    logger.info("Returning %d ticket(s)", len(tickets))
    return TicketListResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        count=len(tickets),
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return a single ticket by ID."""
    logger.info("Fetching ticket %s", ticket_id)
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        logger.warning("Ticket %s not found", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")
    logger.debug("Ticket %s: title=%s, status=%s", ticket_id, ticket.title, ticket.status)
    return TicketResponse.model_validate(ticket)


@router.post("/tickets/{ticket_id}/tags", response_model=TicketResponse)
async def update_ticket_tags(
    ticket_id: uuid.UUID,
    body: UpdateTagsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manually update tags on a ticket (override LLM-generated tags)."""
    logger.info("Updating tags for ticket %s with %d tag(s)", ticket_id, len(body.tags))
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        logger.warning("Ticket %s not found for tag update", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_tags = ticket.tags
    ticket.tags = [tag.model_dump() for tag in body.tags]
    ticket.last_updated = datetime.now(timezone.utc)
    await db.flush()
    logger.info(
        "Tags updated for ticket %s: %s -> %s",
        ticket_id,
        old_tags,
        ticket.tags,
    )
    return TicketResponse.model_validate(ticket)


@router.post("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: uuid.UUID,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update the status of a ticket."""
    logger.info("Updating status for ticket %s to '%s'", ticket_id, body.status.value)
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        logger.warning("Ticket %s not found for status update", ticket_id)
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_status = ticket.status
    ticket.status = body.status.value
    ticket.last_updated = datetime.now(timezone.utc)
    await db.flush()
    logger.info("Status updated for ticket %s: %s -> %s", ticket_id, old_status, ticket.status)
    return TicketResponse.model_validate(ticket)
