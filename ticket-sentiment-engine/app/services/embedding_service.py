"""Embedding service — provider-aware, configurable via EMBEDDING_PROVIDER."""

import logging

from openai import AsyncOpenAI

from app.config import EmbeddingProviderType, settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates text embeddings using the configured provider."""

    def __init__(self) -> None:
        match settings.embedding_provider:
            case EmbeddingProviderType.OPENAI:
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                self.base_url = None
            case EmbeddingProviderType.LOCAL:
                self.client = AsyncOpenAI(
                    base_url=f"{settings.local_llm_base_url}/v1",
                    api_key="not-needed",
                )
            case _:
                raise ValueError(
                    f"Unknown EMBEDDING_PROVIDER: {settings.embedding_provider}"
                )
        self.model = settings.embedding_model

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
