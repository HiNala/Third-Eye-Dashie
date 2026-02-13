"""Load LLM prompts from external files for easy customization.

Prompts live in the prompts/ directory as markdown files.
Uses string.Template ($variable syntax) to avoid conflicts with
JSON curly braces in the prompt templates.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from string import Template

from app.config import settings

logger = logging.getLogger("app.services.llm.prompts")


@lru_cache(maxsize=1)
def load_system_prompt() -> str:
    """Load the system prompt from prompts/system.md. Cached after first read."""
    path = Path(settings.prompt_dir) / "system.md"
    logger.info("Loading system prompt from %s", path)
    return path.read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def load_user_template() -> str:
    """Load the user prompt template from prompts/user_template.md. Cached after first read."""
    path = Path(settings.prompt_dir) / "user_template.md"
    logger.info("Loading user prompt template from %s", path)
    return path.read_text(encoding="utf-8").strip()


def build_user_prompt(content: str, tag_schema: dict) -> str:
    """Build the user prompt by substituting ticket content and tag schema into the template."""
    template = Template(load_user_template())
    return template.safe_substitute(
        tag_schema=json.dumps(tag_schema, indent=2),
        content=content,
    )
