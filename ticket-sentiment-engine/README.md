# Ticket Sentiment Engine

AI-powered backend service that ingests customer support tickets, runs sentiment analysis and demographic extraction via LLM, and exposes REST APIs for the frontend dashboard.

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- An OpenAI API key (or Anthropic key, or local Ollama instance)

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your API key(s)
```

### 3. Start everything

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** (with pgvector) on port `5432`
- **App server** on port `8000`

### 4. Seed sample data

```bash
pip install httpx  # if not already installed
python scripts/seed.py
```

### 5. Explore the API

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Local Development (without Docker)

```bash
# Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure PostgreSQL with pgvector is running locally
# then start the server:
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/tickets` | Get all tickets |
| GET | `/api/v1/tickets/{id}` | Get a single ticket |
| POST | `/api/v1/tickets/{id}/tags` | Update ticket tags |
| POST | `/api/v1/tickets/{id}/status` | Update ticket status |
| POST | `/api/v1/ingest` | Ingest tickets for processing |
| POST | `/api/v1/tickets/search` | Semantic search over tickets |
| GET | `/health` | Health check |

## Switching LLM Providers

Set `LLM_PROVIDER` in `.env`:

- `openai` — OpenAI (default, requires `OPENAI_API_KEY`)
- `anthropic` — Anthropic (requires `ANTHROPIC_API_KEY`)
- `local` — Ollama / vLLM / any OpenAI-compatible API (set `LOCAL_LLM_BASE_URL`)

Embedding provider is configured separately via `EMBEDDING_PROVIDER`.

## Testing

The project has both unit tests and integration tests.

### Unit Tests (no Docker required)

Tests Pydantic schemas, config loading, tag schema validation, and the LLM provider abstraction using a mock provider. Fast and self-contained.

```bash
source thirdeyedashie/bin/activate
pytest tests/ -m "not integration" -v
```

### Integration Tests (requires Docker app running)

Tests the full API against the live Docker app — ingestion, retrieval, tag/status updates, search, and health checks.

```bash
# Make sure the app is running first:
docker compose up --build

# Then in another terminal:
source thirdeyedashie/bin/activate
pytest tests/test_integration.py -v
```

### Run All Tests

```bash
pytest tests/ -v
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures (mock provider, tag schema)
├── mock_llm.py              # Mock LLM provider (keyword-based, no API calls)
├── test_config.py           # Settings, tag schema, enums
├── test_tickets.py          # Pydantic schema validation
├── test_ingest.py           # Ingestion schema validation
├── test_llm_providers.py    # Mock LLM: sentiment, demographics, embeddings
└── test_integration.py      # Live API tests against Docker app
```

## Architecture

See [PRD.md](PRD.md) for the full product requirements document.
