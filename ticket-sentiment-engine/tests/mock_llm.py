"""Mock LLM provider for testing — no external API calls needed."""

from app.schemas.ticket import (
    Demographics,
    DemographicField,
    EmotionalToneValue,
    SentimentValue,
    TagItem,
)
from app.services.llm.base import AnalysisResult, LLMProvider


class MockLLMProvider(LLMProvider):
    """Returns deterministic analysis results for testing."""

    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        # Simple keyword-based mock logic
        content_lower = content.lower()

        if any(w in content_lower for w in ["angry", "frustrated", "unacceptable", "refund"]):
            sentiment = SentimentValue.NEGATIVE
            tone = EmotionalToneValue.FRUSTRATED
        elif any(w in content_lower for w in ["love", "great", "happy", "delighted"]):
            sentiment = SentimentValue.POSITIVE
            tone = EmotionalToneValue.HAPPY
        else:
            sentiment = SentimentValue.NEUTRAL
            tone = EmotionalToneValue.NEUTRAL

        tags = [
            TagItem(category="sentiment", value=sentiment.value),
            TagItem(category="emotional_tone", value=tone.value),
            TagItem(category="priority", value="normal"),
        ]

        demographics = Demographics(
            family_status=DemographicField(value=None, confidence=0.0),
            health_conditions=DemographicField(value=None, confidence=0.0),
            location=DemographicField(value=None, confidence=0.0),
            occupation=DemographicField(value=None, confidence=0.0),
            age_bracket=DemographicField(value=None, confidence=0.0),
        )

        # Extract simple demographic hints
        if "kids" in content_lower or "mom" in content_lower:
            demographics.family_status = DemographicField(value="has kids", confidence=0.8)
        if "migraine" in content_lower:
            demographics.health_conditions = DemographicField(value="migraines", confidence=0.9)
        if "developer" in content_lower:
            demographics.occupation = DemographicField(value="developer", confidence=0.9)

        return AnalysisResult(
            sentiment=sentiment,
            emotional_tone=tone,
            confidence=0.85,
            tags=tags,
            demographics=demographics,
        )

    async def generate_embedding(self, text: str) -> list[float]:
        """Return a deterministic fake embedding vector (1536 dimensions)."""
        # Use a simple hash-based approach for reproducible vectors
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        # Expand to 1536 floats between -1 and 1
        vector = []
        for i in range(1536):
            byte_val = h[i % len(h)]
            vector.append((byte_val / 127.5) - 1.0)
        return vector
