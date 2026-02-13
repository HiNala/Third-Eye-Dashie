"""Ticket processing pipeline — orchestrates LLM analysis and embedding generation."""

import asyncio
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import load_tag_schema
from app.db.session import async_session_factory
from app.models.ticket import Ticket, TicketEmbedding
from app.services.embedding_service import get_embedding_service
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)


async def process_ticket(ticket_id: uuid.UUID) -> None:
    """Background task: run LLM analysis and embedding generation for a ticket.

    This function creates its own DB session since it runs outside the
    request lifecycle (via FastAPI BackgroundTasks).
    """
    llm = get_llm_provider()
    embedder = get_embedding_service()
    tag_schema = load_tag_schema()

    async with async_session_factory() as session:
        # Fetch the ticket
        result = await session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket is None:
            logger.error("Ticket %s not found for processing", ticket_id)
            return

        logger.info("Processing ticket %s: %s", ticket_id, ticket.title)

        try:
            # Run analysis and embedding generation concurrently
            analysis_task = llm.analyze_ticket(ticket.content, tag_schema)
            embedding_task = embedder.generate_embedding(ticket.content)

            analysis, embedding_vector = await asyncio.gather(
                analysis_task, embedding_task
            )

            # Update ticket with analysis results
            ticket.sentiment = analysis.sentiment.value
            ticket.emotional_tone = analysis.emotional_tone.value
            ticket.confidence = analysis.confidence
            ticket.tags = [tag.model_dump() for tag in analysis.tags]
            ticket.demographics = (
                analysis.demographics.model_dump() if analysis.demographics else None
            )

            # Upsert the embedding
            existing_embedding = await session.get(TicketEmbedding, ticket_id)
            if existing_embedding:
                existing_embedding.embedding = embedding_vector
            else:
                session.add(
                    TicketEmbedding(id=ticket_id, embedding=embedding_vector)
                )

            await session.commit()
            logger.info("Successfully processed ticket %s", ticket_id)

        except Exception:
            logger.exception("Failed to process ticket %s", ticket_id)
            await session.rollback()


async def process_tickets_batch(ticket_ids: list[uuid.UUID]) -> None:
    """Process multiple tickets sequentially.

    Sequential to avoid overwhelming the LLM API with concurrent calls.
    For rev2, consider a proper task queue with rate limiting.
    """
    for ticket_id in ticket_ids:
        await process_ticket(ticket_id)
