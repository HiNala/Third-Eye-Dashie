"""Factory that returns the correct LLM provider based on config."""

from app.config import LLMProviderType, settings
from app.services.llm.base import LLMProvider


def get_llm_provider() -> LLMProvider:
    """Return an LLM provider instance based on the LLM_PROVIDER env var."""
    match settings.llm_provider:
        case LLMProviderType.OPENAI:
            from app.services.llm.openai_provider import OpenAIProvider
            return OpenAIProvider()

        case LLMProviderType.ANTHROPIC:
            from app.services.llm.anthropic_provider import AnthropicProvider
            return AnthropicProvider()

        case LLMProviderType.LOCAL:
            from app.services.llm.local_provider import LocalProvider
            return LocalProvider()

        case _:
            raise ValueError(
                f"Unknown LLM_PROVIDER: {settings.llm_provider}. "
                f"Must be one of: openai, anthropic, local"
            )
