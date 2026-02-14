# Third-Eye-Dashie

An AI-powered customer support ticket analysis platform. Ingest support tickets, automatically extract sentiment, emotional tone, topic tags, and customer demographics using LLMs, then explore everything through a modern dashboard with semantic search.

## Architecture

```
┌─────────────────────┐      ┌─────────────────────────┐      ┌──────────────────┐
│   Next.js Dashboard │◄────►│   FastAPI Backend        │◄────►│  PostgreSQL      │
│   (React 19, TS)    │ REST │   (Async, Pydantic v2)   │      │  + pgvector      │
│   port 3000         │      │   port 8000              │      │  port 5432       │
└─────────────────────┘      └────────┬──────────────────┘      └──────────────────┘
                                      │
                              ┌───────┴────────┐
                              │  LLM Provider   │
                              │  (pluggable)    │
                              ├────────────────┤
                              │ OpenAI          │
                              │ Anthropic       │
                              │ Ollama / local  │
                              └────────────────┘
```

**Two-table data model** — raw customer tickets are stored separately from LLM-generated analysis, keeping the source of truth immutable and allowing safe re-processing at any time.

## Features

- **Ticket ingestion** via REST webhook with async background processing
- **Sentiment analysis** — positive / negative / neutral with confidence scores
- **Emotional tone detection** — angry, frustrated, happy, delighted, neutral
- **Tag extraction** using a controlled vocabulary (enforced via YAML schema)
- **Demographic extraction** — family status, health conditions, location, occupation, age bracket (only from information customers explicitly share)
- **Semantic search** over tickets powered by pgvector embeddings
- **Pluggable LLM providers** — switch between OpenAI, Anthropic, or local models with a single env var
- **Dashboard** — ticket list, detail views, sentiment/emotion charts, filtering, dark/light theme

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI (async), SQLAlchemy + asyncpg, Pydantic v2, Alembic |
| Database | PostgreSQL 16 with pgvector extension |
| LLM | OpenAI GPT-4o-mini (default), Anthropic Claude, or Ollama / vLLM |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dimensions) |
| Infrastructure | Docker, Docker Compose |

## Project Structure

```
Third-Eye-Dashie/
├── docker-compose.yml                 # Orchestrates all services
│
├── ticket-sentiment-engine/           # Python backend
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Env-based settings
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── api/routes/                # REST endpoints
│   │   ├── services/
│   │   │   ├── processing.py          # Ingestion pipeline orchestration
│   │   │   ├── embedding_service.py   # Vector embedding generation
│   │   │   └── llm/                   # Pluggable LLM providers
│   │   └── db/                        # Async DB session & base
│   ├── alembic/                       # Database migrations
│   ├── prompts/                       # LLM prompt templates
│   ├── scripts/                       # Seed data scripts
│   ├── tests/                         # Unit + integration tests
│   ├── tag_schema.yaml                # Controlled tag vocabulary
│   ├── requirements.txt
│   └── Dockerfile
│
└── customer-ticket-dashboard/         # Next.js frontend
    ├── app/                           # App Router pages
    │   ├── page.tsx                   # Dashboard home
    │   └── tickets/                   # Ticket list + detail views
    ├── components/                    # UI components (shadcn/ui)
    ├── hooks/                         # React data hooks
    ├── lib/                           # API client, types, utilities
    ├── package.json
    └── Dockerfile
```

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- An API key for your chosen LLM provider (OpenAI by default)

### 1. Clone and configure

```bash
git clone https://github.com/<your-username>/Third-Eye-Dashie.git
cd Third-Eye-Dashie

# Set up backend environment
cp ticket-sentiment-engine/.env.example ticket-sentiment-engine/.env
```

Edit `ticket-sentiment-engine/.env` and add your API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 2. Start all services

```bash
docker compose up --build
```

This launches:

| Service | URL |
|---|---|
| Frontend dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### 3. Seed sample data

In a separate terminal:

```bash
cd ticket-sentiment-engine
pip install httpx
python scripts/seed.py
```

For larger datasets:

```bash
python scripts/seed_100_tickets.py     # 100 generated tickets
python scripts/seed_real_tickets.py    # realistic ticket content
```

### 4. Open the dashboard

Navigate to http://localhost:3000 to see tickets, sentiment analysis, and demographic insights.

## API Reference

Base path: `/api/v1`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tickets` | List all tickets |
| `GET` | `/tickets/{id}` | Get a single ticket with analysis |
| `POST` | `/tickets/{id}/tags` | Update ticket tags (manual override) |
| `POST` | `/tickets/{id}/status` | Update ticket status |
| `POST` | `/ingest` | Ingest tickets for async LLM processing |
| `POST` | `/tickets/search` | Semantic search across tickets |
| `GET` | `/health` | Health check |

Full interactive documentation is available at http://localhost:8000/docs when the backend is running.

## Processing Pipeline

```
POST /api/v1/ingest
        │
        ▼
  Validate & persist to raw_tickets
        │
        ▼
  Background task (async)
   ┌────┴─────┐
   ▼          ▼
 Generate   LLM analysis
 embedding  (sentiment, tags, demographics)
   │          │
   ▼          ▼
 ticket_    processed_tickets
 embeddings
        │
        ▼
  Ticket ready for queries
```

Ingestion returns `202 Accepted` immediately — LLM processing happens in the background so the caller isn't blocked.

## Configuration

### LLM Provider

Set `LLM_PROVIDER` in `ticket-sentiment-engine/.env`:

| Provider | Env Var | Requires |
|---|---|---|
| OpenAI (default) | `LLM_PROVIDER=openai` | `OPENAI_API_KEY` |
| Anthropic | `LLM_PROVIDER=anthropic` | `ANTHROPIC_API_KEY` |
| Local (Ollama/vLLM) | `LLM_PROVIDER=local` | `LOCAL_LLM_BASE_URL` |

Embedding provider is configured independently via `EMBEDDING_PROVIDER` — you can mix and match (e.g., local LLM with OpenAI embeddings).

### All Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tickets_db

# LLM
LLM_PROVIDER=openai                        # openai | anthropic | local
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LOCAL_LLM_BASE_URL=http://localhost:11434

# Embeddings
EMBEDDING_PROVIDER=openai                   # openai | local
EMBEDDING_MODEL=text-embedding-3-small

# App
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO                              # DEBUG | INFO | WARNING | ERROR
```

## Local Development

### Backend

```bash
cd ticket-sentiment-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL + pgvector is running, then:
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd customer-ticket-dashboard
pnpm install
pnpm dev
```

The frontend runs at http://localhost:3000. Set `NEXT_PUBLIC_USE_MOCK=true` during build to use mock data without the backend.

## Testing

### Unit tests (no Docker required)

```bash
cd ticket-sentiment-engine
pytest tests/ -m "not integration" -v
```

Tests cover Pydantic schemas, config loading, tag schema validation, and the LLM provider abstraction using a mock provider.

### Integration tests (requires running services)

```bash
# Start the app first
docker compose up --build

# In another terminal
cd ticket-sentiment-engine
pytest tests/test_integration.py -v
```

## License

This project is for personal/portfolio use.
