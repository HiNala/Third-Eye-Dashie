"""OpenAI LLM provider implementation."""

import json
import logging
import time

from openai import AsyncOpenAI

from app.config import settings
from app.services.llm.base import AnalysisResult, LLMProvider

logger = logging.getLogger("app.services.llm.openai")

SYSTEM_PROMPT = """You are a customer support ticket analysis engine.
Analyze the ticket content and extract:
1. Sentiment (positive, negative, neutral)
2. Emotional tone (angry, happy, frustrated, delighted, neutral)
3. A confidence score (0.0 to 1.0) for your analysis
4. Tags from the allowed categories and values provided
5. Demographic information ONLY if the customer voluntarily mentions it

IMPORTANT: Only use tag values from the allowed schema provided.
For demographics, only extract what is explicitly mentioned — do NOT infer."""


def _build_user_prompt(content: str, tag_schema: dict) -> str:
    return f"""Analyze the following customer support ticket.

ALLOWED TAG SCHEMA:
{json.dumps(tag_schema, indent=2)}

TICKET CONTENT:
{content}

Return your analysis as JSON matching this exact structure:
{{
  "sentiment": "positive|negative|neutral",
  "emotional_tone": "angry|happy|frustrated|delighted|neutral",
  "confidence": 0.0-1.0,
  "tags": [
    {{"category": "<category from schema>", "value": "<value from schema>"}}
  ],
  "demographics": {{
    "family_status": {{"value": "<string or null>", "confidence": 0.0-1.0}},
    "health_conditions": {{"value": "<string or null>", "confidence": 0.0-1.0}},
    "location": {{"value": "<string or null>", "confidence": 0.0-1.0}},
    "occupation": {{"value": "<string or null>", "confidence": 0.0-1.0}},
    "age_bracket": {{"value": "<string or null>", "confidence": 0.0-1.0}}
  }}
}}

If a demographic field is not mentioned, set its value to null and confidence to 0.0."""


class OpenAIProvider(LLMProvider):
    """OpenAI-backed LLM provider using structured JSON output."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.embedding_model = settings.embedding_model
        logger.info("OpenAI provider initialized: llm_model=%s, embedding_model=%s", self.model, self.embedding_model)

    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        logger.debug("Sending analysis request to OpenAI (model=%s, content_length=%d)", self.model, len(content))

        start = time.perf_counter()
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(content, tag_schema)},
            ],
            temperature=0.1,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        raw = response.choices[0].message.content
        usage = response.usage
        logger.info(
            "OpenAI analysis response in %.1fms (tokens: prompt=%d, completion=%d, total=%d)",
            elapsed_ms,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
            usage.total_tokens if usage else 0,
        )
        logger.debug("OpenAI raw response: %s", raw)

        data = json.loads(raw)
        result = AnalysisResult.model_validate(data)
        return result

    async def generate_embedding(self, text: str) -> list[float]:
        logger.debug("Generating embedding (model=%s, text_length=%d)", self.embedding_model, len(text))

        start = time.perf_counter()
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        embedding = response.data[0].embedding
        logger.info("Embedding generated in %.1fms (dims=%d)", elapsed_ms, len(embedding))
        return embedding
