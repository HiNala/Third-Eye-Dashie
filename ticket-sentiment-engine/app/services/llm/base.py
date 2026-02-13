"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from app.schemas.ticket import Demographics, EmotionalToneValue, SentimentValue, TagItem


class AnalysisResult(BaseModel):
    """Structured output that every LLM provider must return."""

    sentiment: SentimentValue
    emotional_tone: EmotionalToneValue
    confidence: float = Field(ge=0.0, le=1.0)
    tags: list[TagItem]
    demographics: Demographics | None = None


class LLMProvider(ABC):
    """Interface that all LLM providers must implement."""

    @abstractmethod
    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        """Analyze a ticket's content and return structured sentiment,
        tags, and demographics."""
        ...

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        ...
