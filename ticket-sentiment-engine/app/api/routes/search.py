"""Semantic search endpoint using pgvector."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ticket import Ticket, TicketEmbedding
from app.schemas.ticket import SearchRequest, SearchResponse, TicketResponse
from app.services.embedding_service import get_embedding_service

router = APIRouter()


@router.post("/tickets/search", response_model=SearchResponse)
async def search_tickets(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search over tickets using pgvector cosine similarity.

    Generates an embedding for the query, then finds the closest
    ticket embeddings in the database.
    """
    embedder = get_embedding_service()

    try:
        query_embedding = await embedder.generate_embedding(body.query)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate query embedding: {e}",
        )

    # pgvector cosine distance: <=> operator (lower = more similar)
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

    return SearchResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        count=len(tickets),
    )
