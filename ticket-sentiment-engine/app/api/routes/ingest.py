"""Ticket ingestion webhook endpoint."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import IngestRequest, IngestResponse
from app.services.processing import process_tickets_batch

logger = logging.getLogger("app.api.ingest")
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
    logger.info("Ingestion request received: %d ticket(s)", len(body.tickets))
    ticket_ids = []

    for i, item in enumerate(body.tickets):
        ticket = Ticket(
            title=item.title,
            content=item.content,
            customer_email=item.customer_email,
            status=item.status.value,
        )
        db.add(ticket)
        await db.flush()  # populate ticket.id
        ticket_ids.append(ticket.id)
        logger.info(
            "  [%d/%d] Persisted ticket %s: title=%r, email=%s",
            i + 1,
            len(body.tickets),
            ticket.id,
            item.title[:60],
            item.customer_email,
        )

    # Commit so the background task can read the tickets
    await db.commit()
    logger.info("All %d ticket(s) committed to DB", len(ticket_ids))

    # Queue background processing
    background_tasks.add_task(process_tickets_batch, ticket_ids)
    logger.info("Background processing queued for %d ticket(s)", len(ticket_ids))

    return IngestResponse(
        accepted=True,
        ticket_ids=ticket_ids,
        message=f"{len(ticket_ids)} ticket(s) queued for processing",
    )
