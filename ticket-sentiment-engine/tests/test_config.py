"""Unit tests for configuration and tag schema loading."""

from app.config import LLMProviderType, EmbeddingProviderType, load_tag_schema, settings


def test_settings_loaded():
    """Settings object loads with defaults."""
    assert settings.app_port == 8000
    assert settings.llm_provider in list(LLMProviderType)
    assert settings.embedding_provider in list(EmbeddingProviderType)


def test_tag_schema_loads():
    """tag_schema.yaml loads and contains expected categories."""
    schema = load_tag_schema()
    assert "sentiment" in schema
    assert "emotional_tone" in schema
    assert "priority" in schema
    assert "positive" in schema["sentiment"]
    assert "negative" in schema["sentiment"]
    assert "neutral" in schema["sentiment"]


def test_tag_schema_emotional_tones():
    """Emotional tone category has expected values."""
    schema = load_tag_schema()
    tones = schema["emotional_tone"]
    assert "angry" in tones
    assert "happy" in tones
    assert "frustrated" in tones
    assert "delighted" in tones
    assert "neutral" in tones


def test_tag_schema_priorities():
    """Priority category has expected values."""
    schema = load_tag_schema()
    priorities = schema["priority"]
    assert "urgent" in priorities
    assert "high" in priorities
    assert "normal" in priorities
    assert "low" in priorities


def test_llm_provider_enum():
    """LLMProviderType enum has all expected values."""
    assert LLMProviderType.OPENAI == "openai"
    assert LLMProviderType.ANTHROPIC == "anthropic"
    assert LLMProviderType.LOCAL == "local"


def test_embedding_provider_enum():
    """EmbeddingProviderType enum has expected values."""
    assert EmbeddingProviderType.OPENAI == "openai"
    assert EmbeddingProviderType.LOCAL == "local"
