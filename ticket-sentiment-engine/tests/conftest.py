"""Shared test fixtures."""

import pytest

from app.config import load_tag_schema
from tests.mock_llm import MockLLMProvider


@pytest.fixture
def mock_provider():
    """Mock LLM provider — no external API calls."""
    return MockLLMProvider()


@pytest.fixture
def tag_schema():
    """Load the controlled tag vocabulary."""
    return load_tag_schema()
