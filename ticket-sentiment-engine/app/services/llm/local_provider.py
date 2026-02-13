"""Local / Ollama-compatible LLM provider implementation.

Uses the OpenAI-compatible API that Ollama (and vLLM, LM Studio, etc.) expose.
"""

import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.services.llm.base import AnalysisResult, LLMProvider
from app.services.llm.prompt_loader import build_user_prompt, load_system_prompt

logger = logging.getLogger(__name__)


class LocalProvider(LLMProvider):
    """Local LLM provider using an OpenAI-compatible API (Ollama, vLLM, etc.)."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url=f"{settings.local_llm_base_url}/v1",
            api_key="not-needed",
        )
        self.model = settings.llm_model

    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": load_system_prompt()},
                {"role": "user", "content": build_user_prompt(content, tag_schema)},
            ],
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        logger.debug("Local LLM raw analysis response: %s", raw)
        data = json.loads(raw)
        return AnalysisResult.model_validate(data)

    async def generate_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=text,
        )
        return response.data[0].embedding
