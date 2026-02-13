"""Semantic search endpoint using pgvector."""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.ticket import ProcessedTicket, RawTicket, TicketEmbedding
from app.schemas.ticket import (
    ProcessingStatus,
    SearchRequest,
    SearchResponse,
    TicketResponse,
)
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger("app.api.search")
router = APIRouter()


def _build_search_result(raw: RawTicket, processed: ProcessedTicket) -> TicketResponse:
    """Build a TicketResponse from a raw+processed pair found via search."""
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


@router.post("/tickets/search", response_model=SearchResponse)
async def search_tickets(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search over tickets using pgvector cosine similarity.

    Joins TicketEmbedding -> ProcessedTicket -> RawTicket to return
    full ticket data ranked by embedding similarity.
    """
    logger.info("Search request: query=%r, limit=%d", body.query, body.limit)

    embedder = get_embedding_service()

    try:
        start = time.perf_counter()
        query_embedding = await embedder.generate_embedding(body.query)
        embed_ms = (time.perf_counter() - start) * 1000
        logger.info("Query embedding generated in %.1fms (dims=%d)", embed_ms, len(query_embedding))
    except Exception as e:
        logger.error("Failed to generate query embedding: %s", e, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate query embedding: {e}",
        )

    # pgvector cosine distance: <=> operator (lower = more similar)
    # Join: TicketEmbedding -> ProcessedTicket -> RawTicket
    start = time.perf_counter()
    stmt = (
        select(RawTicket, ProcessedTicket)
        .join(ProcessedTicket, RawTicket.id == ProcessedTicket.raw_ticket_id)
        .join(TicketEmbedding, ProcessedTicket.id == TicketEmbedding.id)
        .order_by(
            TicketEmbedding.embedding.cosine_distance(query_embedding)
        )
        .limit(body.limit)
    )

    result = await db.execute(stmt)
    rows = result.all()
    search_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "Search completed: %d result(s) in %.1fms",
        len(rows),
        search_ms,
    )
    for i, (raw, processed) in enumerate(rows):
        logger.debug(
            "  [%d] %s — %s / %s",
            i + 1,
            raw.title,
            processed.sentiment,
            processed.emotional_tone,
        )

    tickets = [_build_search_result(raw, processed) for raw, processed in rows]
    return SearchResponse(
        tickets=tickets,
        count=len(tickets),
    )
