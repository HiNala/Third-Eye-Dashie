"""Anthropic LLM provider implementation."""

import json
import logging

from anthropic import AsyncAnthropic

from app.config import settings
from app.services.llm.base import AnalysisResult, LLMProvider
from app.services.llm.prompt_loader import build_user_prompt, load_system_prompt

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic-backed LLM provider."""

    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model or "claude-sonnet-4-20250514"

    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=load_system_prompt(),
            messages=[
                {"role": "user", "content": build_user_prompt(content, tag_schema)},
            ],
            temperature=0.1,
        )
        raw = message.content[0].text
        logger.debug("Anthropic raw analysis response: %s", raw)
        data = json.loads(raw)
        return AnalysisResult.model_validate(data)

    async def generate_embedding(self, text: str) -> list[float]:
        # Anthropic doesn't offer an embeddings API — fall back to OpenAI
        # or a local provider for embeddings when using Anthropic for LLM.
        raise NotImplementedError(
            "Anthropic does not provide an embeddings API. "
            "Set EMBEDDING_PROVIDER=openai or EMBEDDING_PROVIDER=local."
        )
