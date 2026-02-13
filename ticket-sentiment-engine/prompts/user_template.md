Analyze the following customer support ticket.

ALLOWED TAG SCHEMA:
${tag_schema}

TICKET CONTENT:
${content}

Return your analysis as JSON matching this exact structure:
{
  "sentiment": "positive|negative|neutral",
  "emotional_tone": "angry|happy|frustrated|delighted|neutral",
  "confidence": 0.0-1.0,
  "tags": [
    {"category": "<category from schema>", "value": "<value from schema>"}
  ],
  "demographics": {
    "family_status": {"value": "<string or null>", "confidence": 0.0-1.0},
    "health_conditions": {"value": "<string or null>", "confidence": 0.0-1.0},
    "location": {"value": "<string or null>", "confidence": 0.0-1.0},
    "occupation": {"value": "<string or null>", "confidence": 0.0-1.0},
    "age_bracket": {"value": "<string or null>", "confidence": 0.0-1.0}
  }
}

If a demographic field is not mentioned, set its value to null and confidence to 0.0.
Return ONLY valid JSON — no other text.
