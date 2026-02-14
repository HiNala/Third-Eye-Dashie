"""Application configuration loaded from environment variables."""

from enum import Enum
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class EmbeddingProviderType(str, Enum):
    OPENAI = "openai"
    LOCAL = "local"


class Settings(BaseSettings):
    """App-wide settings, loaded from .env or environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tickets_db"

    # LLM
    llm_provider: LLMProviderType = LLMProviderType.OPENAI
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    local_llm_base_url: str = "http://localhost:11434"

    # Embeddings
    embedding_provider: EmbeddingProviderType = EmbeddingProviderType.OPENAI
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Tag schema path (relative to this file's parent directory)
    tag_schema_path: str = str(Path(__file__).resolve().parent.parent / "tag_schema.yaml")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()


def load_tag_schema() -> dict:
    """Load the controlled vocabulary for ticket tags from YAML."""
    with open(settings.tag_schema_path, "r") as f:
        return yaml.safe_load(f)
