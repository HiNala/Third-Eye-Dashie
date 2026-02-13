"""Semantic search endpoint using pgvector."""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ticket import Ticket, TicketEmbedding
from app.schemas.ticket import SearchRequest, SearchResponse, TicketResponse
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger("app.api.search")
router = APIRouter()


@router.post("/tickets/search", response_model=SearchResponse)
async def search_tickets(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search over tickets using pgvector cosine similarity."""
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
    start = time.perf_counter()
    stmt = (
        select(Ticket)
        .join(TicketEmbedding, Ticket.id == TicketEmbedding.id)
        .order_by(
            TicketEmbedding.embedding.cosine_distance(query_embedding)
        )
        .limit(body.limit)
    )

    result = await db.execute(stmt)
    tickets = result.scalars().all()
    search_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "Search completed: %d result(s) in %.1fms",
        len(tickets),
        search_ms,
    )
    for i, t in enumerate(tickets):
        logger.debug("  [%d] %s — %s / %s", i + 1, t.title, t.sentiment, t.emotional_tone)

    return SearchResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        count=len(tickets),
    )
