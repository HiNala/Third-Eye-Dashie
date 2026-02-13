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

## Architecture

See [PRD.md](PRD.md) for the full product requirements document.
