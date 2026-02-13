"""Ticket ingestion webhook endpoint."""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import IngestRequest, IngestResponse
from app.services.processing import process_tickets_batch

router = APIRouter()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_tickets(
    body: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Ingest one or more tickets for sentiment processing.

    Tickets are persisted immediately and LLM processing is
    dispatched as a background task. Returns 202 Accepted.
    """
    ticket_ids = []

    for item in body.tickets:
        ticket = Ticket(
            title=item.title,
            content=item.content,
            customer_email=item.customer_email,
            status=item.status.value,
        )
        db.add(ticket)
        await db.flush()  # populate ticket.id
        ticket_ids.append(ticket.id)

    # Commit so the background task can read the tickets
    await db.commit()

    # Queue background processing
    background_tasks.add_task(process_tickets_batch, ticket_ids)

    return IngestResponse(
        accepted=True,
        ticket_ids=ticket_ids,
        message=f"{len(ticket_ids)} ticket(s) queued for processing",
    )
