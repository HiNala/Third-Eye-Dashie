"""OpenAI LLM provider implementation."""

import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.services.llm.base import AnalysisResult, LLMProvider

logger = logging.getLogger(__name__)

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

    async def analyze_ticket(
        self, content: str, tag_schema: dict
    ) -> AnalysisResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(content, tag_schema)},
            ],
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        logger.debug("OpenAI raw analysis response: %s", raw)
        data = json.loads(raw)
        return AnalysisResult.model_validate(data)

    async def generate_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return response.data[0].embedding
