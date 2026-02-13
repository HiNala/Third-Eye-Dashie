"""Unit tests for the LLM provider abstraction and mock provider."""

import pytest

from app.config import load_tag_schema
from app.services.llm.base import AnalysisResult
from tests.mock_llm import MockLLMProvider


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_provider():
    return MockLLMProvider()


@pytest.fixture
def tag_schema():
    return load_tag_schema()


async def test_analyze_negative_ticket(mock_provider: MockLLMProvider, tag_schema: dict):
    """Mock provider detects negative sentiment from angry keywords."""
    result = await mock_provider.analyze_ticket(
        "This is unacceptable! I want a refund immediately!",
        tag_schema,
    )
    assert isinstance(result, AnalysisResult)
    assert result.sentiment.value == "negative"
    assert result.emotional_tone.value == "frustrated"
    assert result.confidence > 0
    assert len(result.tags) > 0


async def test_analyze_positive_ticket(mock_provider: MockLLMProvider, tag_schema: dict):
    """Mock provider detects positive sentiment from happy keywords."""
    result = await mock_provider.analyze_ticket(
        "I love this product! Great quality and fast shipping!",
        tag_schema,
    )
    assert result.sentiment.value == "positive"
    assert result.emotional_tone.value == "happy"


async def test_analyze_neutral_ticket(mock_provider: MockLLMProvider, tag_schema: dict):
    """Mock provider returns neutral for ambiguous content."""
    result = await mock_provider.analyze_ticket(
        "Can you tell me the dimensions of product X?",
        tag_schema,
    )
    assert result.sentiment.value == "neutral"
    assert result.emotional_tone.value == "neutral"


async def test_demographics_extraction(mock_provider: MockLLMProvider, tag_schema: dict):
    """Mock provider extracts demographic hints from content."""
    result = await mock_provider.analyze_ticket(
        "I'm a developer and my kids need this for school. I also have migraines.",
        tag_schema,
    )
    assert result.demographics is not None
    assert result.demographics.occupation.value == "developer"
    assert result.demographics.occupation.confidence > 0
    assert result.demographics.family_status.value == "has kids"
    assert result.demographics.health_conditions.value == "migraines"


async def test_demographics_empty_when_not_mentioned(
    mock_provider: MockLLMProvider, tag_schema: dict
):
    """Demographics fields are null when not mentioned in content."""
    result = await mock_provider.analyze_ticket(
        "Can you ship this to me faster please?",
        tag_schema,
    )
    assert result.demographics is not None
    assert result.demographics.occupation.value is None
    assert result.demographics.family_status.value is None


async def test_generate_embedding(mock_provider: MockLLMProvider):
    """Mock provider generates a 1536-dim embedding vector."""
    embedding = await mock_provider.generate_embedding("test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 1536
    assert all(isinstance(v, float) for v in embedding)


async def test_embedding_deterministic(mock_provider: MockLLMProvider):
    """Same input produces same embedding."""
    e1 = await mock_provider.generate_embedding("hello world")
    e2 = await mock_provider.generate_embedding("hello world")
    assert e1 == e2


async def test_embedding_different_for_different_input(mock_provider: MockLLMProvider):
    """Different inputs produce different embeddings."""
    e1 = await mock_provider.generate_embedding("hello world")
    e2 = await mock_provider.generate_embedding("goodbye world")
    assert e1 != e2


async def test_analysis_result_validates_schema():
    """AnalysisResult enforces field constraints."""
    from app.schemas.ticket import SentimentValue, EmotionalToneValue, TagItem

    result = AnalysisResult(
        sentiment=SentimentValue.POSITIVE,
        emotional_tone=EmotionalToneValue.HAPPY,
        confidence=0.95,
        tags=[TagItem(category="sentiment", value="positive")],
        demographics=None,
    )
    assert result.confidence == 0.95
    assert result.tags[0].value == "positive"
