"""Embedding service — provider-aware, configurable via EMBEDDING_PROVIDER."""

import logging
import time

from openai import AsyncOpenAI

from app.config import EmbeddingProviderType, settings

logger = logging.getLogger("app.services.embedding")


class EmbeddingService:
    """Generates text embeddings using the configured provider."""

    def __init__(self) -> None:
        match settings.embedding_provider:
            case EmbeddingProviderType.OPENAI:
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                self.base_url = None
                logger.debug("EmbeddingService using OpenAI provider")
            case EmbeddingProviderType.LOCAL:
                self.client = AsyncOpenAI(
                    base_url=f"{settings.local_llm_base_url}/v1",
                    api_key="not-needed",
                )
                logger.debug("EmbeddingService using local provider at %s", settings.local_llm_base_url)
            case _:
                raise ValueError(
                    f"Unknown EMBEDDING_PROVIDER: {settings.embedding_provider}"
                )
        self.model = settings.embedding_model

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        logger.debug("Generating embedding: model=%s, text_length=%d", self.model, len(text))
        start = time.perf_counter()

        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        embedding = response.data[0].embedding
        logger.info("Embedding generated in %.1fms (model=%s, dims=%d)", elapsed_ms, self.model, len(embedding))
        return embedding


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
