# Ticket Sentiment Engine -- Product Requirements Document

## 1. Overview

A Python-based microservice that lives in `ticket-sentiment-engine/` and provides:

- **Ticket ingestion** (REST + webhook)
- **AI-powered sentiment analysis and demographic extraction** via LLM
- **Persistent storage** (relational DB for structured data, vector DB for semantic search)
- **REST APIs** consumed by the frontend dashboard team

---

## 2. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Framework | **FastAPI** | Async, auto-generated OpenAPI docs, easy for frontend devs to integrate |
| Database | **PostgreSQL** via SQLAlchemy + asyncpg | Robust relational store, JSONB for flexible tag/demographic data |
| Vector DB | **pgvector** (PostgreSQL extension) | Keeps infra simple -- one DB process, semantic search via embeddings |
| Embeddings | **OpenAI `text-embedding-3-small`** (or configurable) | Generates vectors for semantic search on ticket content |
| LLM | **Pluggable via config** (default: OpenAI GPT-4o-mini) | Sentiment + demographic extraction via structured output |
| LLM Abstraction | **LLM Provider Interface** | Swap between OpenAI, Anthropic, local models, etc. via env var |
| Migrations | **Alembic** | Schema versioning |
| Containerization | **Docker + docker-compose** | PostgreSQL + pgvector + app in one command |

---

## 3. Data Model

The data model uses a **two-table architecture** to separate raw customer data from LLM-generated outputs. This keeps the raw data as an immutable source of truth and allows safe re-processing without tainting the original ticket data.

### 3.1 Raw Tickets Table (`raw_tickets`)

Source-of-truth table containing only customer-submitted data. Never mutated by the LLM pipeline.

```
id              UUID        PK, default uuid4
title           TEXT        NOT NULL
content         TEXT        NOT NULL
customer_email  VARCHAR     NOT NULL
status          VARCHAR     "open" | "in_progress" | "closed", default "open"
created_at      TIMESTAMP   auto
last_updated    TIMESTAMP   auto, on-update
```

### 3.2 Processed Tickets Table (`processed_tickets`)

LLM-enriched output table. Each row is linked 1:1 to a raw ticket via `raw_ticket_id`. This record can be deleted and re-created to re-process a ticket without affecting the original data.

```
id              UUID        PK, default uuid4
raw_ticket_id   UUID        FK -> raw_tickets.id, UNIQUE, NOT NULL
sentiment       VARCHAR     "positive" | "negative" | "neutral"
emotional_tone  VARCHAR     "angry" | "happy" | "frustrated" | "delighted" | "neutral"
confidence      FLOAT       LLM confidence score (0.0-1.0)
tags            JSONB       Array of sentiment/topic tags (LLM-generated)
demographics    JSONB       Extracted demographic fields (see 3.5)
processed_at    TIMESTAMP   auto
last_updated    TIMESTAMP   auto, on-update
```

### 3.3 Ticket Embeddings Table (`ticket_embeddings`)

```
id              UUID        PK, FK -> processed_tickets.id
embedding       VECTOR(1536) pgvector column
```

### 3.4 Table Relationships

```
raw_tickets  1 ──── 0..1  processed_tickets  (via raw_ticket_id)
processed_tickets  1 ──── 0..1  ticket_embeddings  (via id)
```

Key design decisions:
- The **raw ticket `id`** is the canonical identifier used by the frontend and all API routes
- **Status** lives on `raw_tickets` (business/workflow field, not an LLM output)
- **Tags** live on `processed_tickets` (both auto-generated and manual overrides)
- **Re-processing is safe**: delete the `processed_tickets` row and re-run the pipeline; raw data is untouched
- **Embeddings link to `processed_tickets`** since they represent the processed/analyzed state
- API responses include a `processing_status` field: `"pending"` (no processed record) or `"completed"`

### 3.5 Tags Schema (LLM must conform to)

Tags are a JSON array of objects. Each tag has a `category` and `value` drawn from a **controlled vocabulary** defined in a config file (`tag_schema.yaml`). This lets the team update allowed tags without code changes.

```yaml
# tag_schema.yaml (example structure, specific values TBD)
sentiment:
  - positive
  - negative
  - neutral
emotional_tone:
  - angry
  - happy
  - frustrated
  - delighted
  - neutral
topics: []       # to be defined later (e.g. shipping, billing, product)
priority:
  - urgent
  - high
  - normal
  - low
```

The LLM prompt will include these allowed values and be instructed to only use them. Tags stored on the ticket look like:

```json
[
  {"category": "sentiment", "value": "negative"},
  {"category": "emotional_tone", "value": "frustrated"},
  {"category": "topics", "value": "shipping"},
  {"category": "priority", "value": "urgent"}
]
```

### 3.6 Demographics Schema

Stored as JSONB on the ticket. Extracted fields with confidence scores:

```json
{
  "family_status": {"value": "has kids ages 5, 8", "confidence": 0.9},
  "health_conditions": {"value": "migraines", "confidence": 0.85},
  "location": {"value": "California", "confidence": 0.7},
  "occupation": {"value": "developer", "confidence": 0.8},
  "age_bracket": {"value": "30-40", "confidence": 0.6}
}
```

Fields are nullable -- only populated when the customer voluntarily shares information.

---

## 4. REST API Specification

Base path: `/api/v1`

### 4.1 Ticket Retrieval

**`GET /api/v1/tickets`**

- Returns all tickets (paginated in rev2)
- Response: `{ "tickets": [Ticket, ...], "count": int }`

**`GET /api/v1/tickets/{ticket_id}`**

- Returns a single ticket by UUID

### 4.2 Ticket Mutation

**`POST /api/v1/tickets/{ticket_id}/tags`**

- Body: `{ "tags": [{"category": "...", "value": "..."}] }`
- Replaces tags on the ticket (manual override)
- Returns: updated Ticket object

**`POST /api/v1/tickets/{ticket_id}/status`**

- Body: `{ "status": "open" | "in_progress" | "closed" }`
- Returns: updated Ticket object

### 4.3 Ingestion Webhook

**`POST /api/v1/ingest`**

- Accepts one or more tickets for processing
- Body:

```json
{
  "tickets": [
    {
      "title": "Order not received",
      "content": "I placed an order 2 weeks ago and...",
      "customer_email": "jane@example.com",
      "status": "open"
    }
  ]
}
```

- **Processing is async**: returns `202 Accepted` with ticket IDs immediately, then runs the LLM pipeline in the background.
- Response:

```json
{
  "accepted": true,
  "ticket_ids": ["uuid-1", "uuid-2"],
  "message": "2 tickets queued for processing"
}
```

### 4.4 Semantic Search (rev1 basic, rev2 robust)

**`POST /api/v1/tickets/search`**

- Body: `{ "query": "customers angry about shipping delays" }`
- Uses pgvector similarity search on ticket embeddings
- Returns: ranked list of matching Ticket objects

---

## 5. Ingestion + Processing Pipeline

```mermaid
flowchart LR
    A[POST /ingest] --> B[Validate + Persist to raw_tickets]
    B --> C[Background Task]
    C --> D[Generate embedding via OpenAI]
    C --> E[LLM: Extract sentiment + tags + demographics]
    D --> F[Store embedding in ticket_embeddings]
    E --> G[Create/update processed_tickets record]
    G --> H[Ticket ready for API queries]
    F --> H
```

The two-table flow ensures raw customer data is never mutated by LLM processing:

1. **Ingestion** (`POST /ingest`) persists tickets to `raw_tickets` only
2. **Background processing** reads from `raw_tickets`, runs LLM analysis + embedding generation
3. **Results** are written to `processed_tickets` (linked via `raw_ticket_id`) and `ticket_embeddings`
4. **API queries** (`GET /tickets`) join `raw_tickets` with `processed_tickets` (left join) to return a unified view

Key design decisions:

- **Background processing via FastAPI BackgroundTasks** (rev1). For rev2 scale, swap to Celery/Redis or an async task queue.
- **LLM structured output**: Use OpenAI function calling / JSON mode to force the LLM response into our tag schema. The system prompt includes `tag_schema.yaml` contents so the LLM knows the allowed values.
- **Embedding generation** happens in parallel with sentiment analysis to reduce latency.
- **Re-processing**: To re-run LLM on a ticket, delete its `processed_tickets` row and re-trigger the pipeline. The raw data is untouched.

---

## 6. Project Structure

```
ticket-sentiment-engine/
  app/
    __init__.py
    main.py              # FastAPI app, startup, lifespan
    config.py            # Settings via pydantic-settings (env vars)
    models/
      __init__.py
      ticket.py          # SQLAlchemy ORM models (RawTicket, ProcessedTicket, TicketEmbedding)
    schemas/
      __init__.py
      ticket.py          # Pydantic request/response schemas
    api/
      __init__.py
      routes/
        __init__.py
        tickets.py       # GET/POST ticket endpoints
        ingest.py        # Webhook ingestion endpoint
        search.py        # Semantic search endpoint
    services/
      __init__.py
      llm/
        __init__.py
        base.py            # Abstract LLMProvider interface
        prompt_loader.py   # Loads prompts from prompts/ directory
        openai_provider.py # OpenAI implementation
        anthropic_provider.py # Anthropic implementation
        local_provider.py  # Local/Ollama implementation
        factory.py         # Returns provider based on LLM_PROVIDER env var
      embedding_service.py  # Embedding generation (also provider-aware)
      processing.py      # Orchestrates the ingestion pipeline
    db/
      __init__.py
      session.py         # Async DB session factory
      base.py            # Declarative base
  prompts/
    system.md            # LLM system prompt (shared by all providers)
    user_template.md     # User prompt template ($tag_schema, $content placeholders)
  alembic/               # DB migrations
  tag_schema.yaml        # Controlled vocabulary for tags
  requirements.txt
  Dockerfile
  docker-compose.yml     # PostgreSQL + pgvector + app
  .env.example           # Required env vars template
  README.md
```

---

## 7. Configuration (.env)

```
# --- Database ---
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tickets_db

# --- LLM Provider (switch providers by changing LLM_PROVIDER) ---
LLM_PROVIDER=openai                   # openai | anthropic | local
LLM_MODEL=gpt-4o-mini                 # model name for the chosen provider
OPENAI_API_KEY=sk-...                  # required if LLM_PROVIDER=openai
ANTHROPIC_API_KEY=sk-ant-...           # required if LLM_PROVIDER=anthropic
LOCAL_LLM_BASE_URL=http://localhost:11434  # required if LLM_PROVIDER=local (e.g. Ollama)

# --- Embedding Provider (can differ from LLM provider) ---
EMBEDDING_PROVIDER=openai              # openai | local
EMBEDDING_MODEL=text-embedding-3-small

# --- App ---
APP_PORT=8000

# --- Prompts (optional, defaults to prompts/ in project root) ---
PROMPT_DIR=prompts                    # directory containing system.md and user_template.md
```

---

## 8. LLM Provider Abstraction

All LLM calls go through a `LLMProvider` interface so the provider can be swapped via a single env var (`LLM_PROVIDER`).

```python
# services/llm/base.py (simplified)
class LLMProvider(ABC):
    @abstractmethod
    async def analyze_ticket(self, content: str, tag_schema: dict) -> AnalysisResult:
        """Return sentiment, tags, demographics for a ticket."""
        ...

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Return embedding vector for semantic search."""
        ...
```

The factory (`services/llm/factory.py`) reads `LLM_PROVIDER` from config and returns the correct implementation:

- **`openai`** -- Uses `openai` SDK with structured outputs / JSON mode
- **`anthropic`** -- Uses `anthropic` SDK with tool_use for structured extraction
- **`local`** -- Hits an OpenAI-compatible API (e.g. Ollama, vLLM) at `LOCAL_LLM_BASE_URL`

Each provider parses LLM responses into a shared `AnalysisResult` Pydantic model, so the rest of the app is provider-agnostic.

### Externalized Prompts

LLM prompts live in the `prompts/` directory as markdown files, not in Python code:

- **`prompts/system.md`** -- System prompt shared by all providers. Defines the analysis task, allowed extractions, and privacy guidelines.
- **`prompts/user_template.md`** -- User prompt template with `$tag_schema` and `$content` placeholders, including the expected JSON output structure.

A shared `prompt_loader.py` utility loads and caches these files at runtime. To customize prompt behavior, edit the markdown files -- no Python code changes required. The prompt directory can be overridden via the `PROMPT_DIR` environment variable.

Embedding provider can be configured independently (`EMBEDDING_PROVIDER`) since you may want a cloud LLM but local embeddings, or vice versa.

---

## 9. Implementation Phases

### Phase 1 -- MVP (this sprint)

- FastAPI project scaffold with Docker + PostgreSQL + pgvector
- Ticket data model + Alembic migrations
- `POST /ingest` webhook with background LLM processing
- `GET /tickets` and `GET /tickets/{id}` endpoints
- `POST /tickets/{id}/tags` and `POST /tickets/{id}/status`
- LLM sentiment analysis + tag extraction with schema enforcement
- Basic demographic extraction
- Basic semantic search endpoint

### Phase 2 -- Hardening

- Pagination, filtering, sorting on `GET /tickets`
- Robust semantic search (hybrid: keyword + vector, faceted filtering)
- Bulk ingestion performance (task queue with Celery/Redis)
- Rate limiting and auth (API key or JWT)
- Customer object expansion (replace `customer_email` with full profile)
- Confidence thresholds and human-review workflow for low-confidence extractions

---

## 10. Key Risks and Decisions

- **LLM tag conformance**: Mitigated by using OpenAI structured outputs (JSON mode / function calling) with explicit enum constraints. A validation layer will reject and retry if the LLM returns out-of-schema tags.
- **Privacy (demographics)**: Only extract what customers explicitly mention. Add a `confidence` score and only surface high-confidence extractions. No inference from external data.
- **Cost**: GPT-4o-mini is cheap (~$0.15/1M input tokens). Embeddings are ~$0.02/1M tokens. At 10K tickets, total LLM cost is under $5.
- **Search quality (rev1)**: Pure vector similarity is a solid starting point. Rev2 adds hybrid search for better precision.
- **Data integrity (two-table split)**: Raw ticket data is stored separately from LLM outputs, ensuring the source of truth is never mutated by the processing pipeline. This allows safe re-processing, auditing, and prevents LLM hallucinations from corrupting customer data.
