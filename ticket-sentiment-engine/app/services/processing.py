"""Ticket processing pipeline — orchestrates LLM analysis and embedding generation."""

import asyncio
import logging
import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import load_tag_schema
from app.db.session import async_session_factory
from app.models.ticket import Ticket, TicketEmbedding
from app.services.embedding_service import get_embedding_service
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger("app.services.processing")


async def process_ticket(ticket_id: uuid.UUID) -> None:
    """Background task: run LLM analysis and embedding generation for a ticket.

    This function creates its own DB session since it runs outside the
    request lifecycle (via FastAPI BackgroundTasks).
    """
    overall_start = time.perf_counter()
    logger.info("[%s] Starting ticket processing", ticket_id)

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
            logger.error("[%s] Ticket not found in DB — aborting", ticket_id)
            return

        logger.info(
            "[%s] Ticket loaded: title=%r, content_length=%d chars, email=%s",
            ticket_id,
            ticket.title[:60],
            len(ticket.content),
            ticket.customer_email,
        )

        try:
            # Run analysis and embedding generation concurrently
            logger.info("[%s] Dispatching LLM analysis + embedding generation", ticket_id)
            analysis_start = time.perf_counter()

            analysis_task = llm.analyze_ticket(ticket.content, tag_schema)
            embedding_task = embedder.generate_embedding(ticket.content)

            analysis, embedding_vector = await asyncio.gather(
                analysis_task, embedding_task
            )
            analysis_ms = (time.perf_counter() - analysis_start) * 1000
            logger.info("[%s] LLM + embedding completed in %.1fms", ticket_id, analysis_ms)

            # Log analysis results
            logger.info(
                "[%s] Analysis results: sentiment=%s, tone=%s, confidence=%.2f",
                ticket_id,
                analysis.sentiment.value,
                analysis.emotional_tone.value,
                analysis.confidence,
            )
            logger.info(
                "[%s] Tags: %s",
                ticket_id,
                [f"{t.category}:{t.value}" for t in analysis.tags],
            )
            if analysis.demographics:
                demo = analysis.demographics
                extracted = {
                    k: v["value"]
                    for k, v in demo.model_dump().items()
                    if v and v.get("value") is not None
                }
                if extracted:
                    logger.info("[%s] Demographics extracted: %s", ticket_id, extracted)
                else:
                    logger.debug("[%s] No demographics found in content", ticket_id)

            logger.info(
                "[%s] Embedding generated: %d dimensions",
                ticket_id,
                len(embedding_vector),
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
                logger.debug("[%s] Updated existing embedding", ticket_id)
            else:
                session.add(
                    TicketEmbedding(id=ticket_id, embedding=embedding_vector)
                )
                logger.debug("[%s] Created new embedding record", ticket_id)

            await session.commit()

            total_ms = (time.perf_counter() - overall_start) * 1000
            logger.info(
                "[%s] Processing complete (%.1fms total) — sentiment=%s, tone=%s",
                ticket_id,
                total_ms,
                analysis.sentiment.value,
                analysis.emotional_tone.value,
            )

        except Exception as e:
            total_ms = (time.perf_counter() - overall_start) * 1000
            logger.exception(
                "[%s] FAILED after %.1fms — %s: %s",
                ticket_id,
                total_ms,
                type(e).__name__,
                e,
            )
            await session.rollback()


async def process_tickets_batch(ticket_ids: list[uuid.UUID]) -> None:
    """Process multiple tickets sequentially.

    Sequential to avoid overwhelming the LLM API with concurrent calls.
    For rev2, consider a proper task queue with rate limiting.
    """
    logger.info(
        "Starting batch processing: %d ticket(s) [%s]",
        len(ticket_ids),
        ", ".join(str(tid)[:8] for tid in ticket_ids),
    )
    batch_start = time.perf_counter()

    for i, ticket_id in enumerate(ticket_ids):
        logger.info("--- Batch progress: %d/%d ---", i + 1, len(ticket_ids))
        await process_ticket(ticket_id)

    batch_ms = (time.perf_counter() - batch_start) * 1000
    logger.info(
        "Batch complete: %d ticket(s) processed in %.1fms (avg %.1fms/ticket)",
        len(ticket_ids),
        batch_ms,
        batch_ms / max(len(ticket_ids), 1),
    )
