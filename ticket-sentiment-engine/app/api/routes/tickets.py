"""Ticket CRUD API routes."""

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

router = APIRouter()


@router.get("/tickets", response_model=TicketListResponse)
async def get_all_tickets(db: AsyncSession = Depends(get_db)):
    """Return all tickets."""
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    tickets = result.scalars().all()
    return TicketListResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        count=len(tickets),
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Return a single ticket by ID."""
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)


@router.post("/tickets/{ticket_id}/tags", response_model=TicketResponse)
async def update_ticket_tags(
    ticket_id: uuid.UUID,
    body: UpdateTagsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Manually update tags on a ticket (override LLM-generated tags)."""
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.tags = [tag.model_dump() for tag in body.tags]
    ticket.last_updated = datetime.now(timezone.utc)
    await db.flush()
    return TicketResponse.model_validate(ticket)


@router.post("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: uuid.UUID,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update the status of a ticket."""
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = body.status.value
    ticket.last_updated = datetime.now(timezone.utc)
    await db.flush()
    return TicketResponse.model_validate(ticket)
