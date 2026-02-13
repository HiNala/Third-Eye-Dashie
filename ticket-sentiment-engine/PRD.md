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
| LLM | **OpenAI GPT-4o-mini** (or configurable) | Sentiment + demographic extraction via structured output |
| Migrations | **Alembic** | Schema versioning |
| Containerization | **Docker + docker-compose** | PostgreSQL + pgvector + app in one command |

---

## 3. Data Model

### 3.1 Ticket Table (`tickets`)

```
id              UUID        PK, default uuid4
title           TEXT        NOT NULL
content         TEXT        NOT NULL
tags            JSONB       Array of sentiment/topic tags (LLM-generated)
demographics    JSONB       Extracted demographic fields (see 3.3)
sentiment       VARCHAR     "positive" | "negative" | "neutral"
emotional_tone  VARCHAR     "angry" | "happy" | "frustrated" | "delighted" | "neutral"
confidence      FLOAT       LLM confidence score (0.0-1.0)
customer_email  VARCHAR     NOT NULL
status          VARCHAR     "open" | "in_progress" | "closed", default "open"
created_at      TIMESTAMP   auto
last_updated    TIMESTAMP   auto, on-update
```

### 3.2 Ticket Embeddings Table (`ticket_embeddings`)

```
id              UUID        PK, FK -> tickets.id
embedding       VECTOR(1536) pgvector column
```

### 3.3 Tags Schema (LLM must conform to)

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

### 3.4 Demographics Schema

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
    A[POST /ingest] --> B[Validate + Persist raw ticket to DB]
    B --> C[Background Task]
    C --> D[Generate embedding via OpenAI]
    C --> E[LLM: Extract sentiment + tags + demographics]
    D --> F[Store embedding in ticket_embeddings]
    E --> G[Update ticket record with tags + demographics]
    G --> H[Ticket ready for API queries]
    F --> H
```

Key design decisions:

- **Background processing via FastAPI BackgroundTasks** (rev1). For rev2 scale, swap to Celery/Redis or an async task queue.
- **LLM structured output**: Use OpenAI function calling / JSON mode to force the LLM response into our tag schema. The system prompt includes `tag_schema.yaml` contents so the LLM knows the allowed values.
- **Embedding generation** happens in parallel with sentiment analysis to reduce latency.

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
      ticket.py          # SQLAlchemy ORM model
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
      llm_service.py     # OpenAI calls for sentiment + demographics
      embedding_service.py  # OpenAI embedding generation
      processing.py      # Orchestrates the ingestion pipeline
    db/
      __init__.py
      session.py         # Async DB session factory
      base.py            # Declarative base
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
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tickets_db
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
APP_PORT=8000
```

---

## 8. Implementation Phases

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

## 9. Key Risks and Decisions

- **LLM tag conformance**: Mitigated by using OpenAI structured outputs (JSON mode / function calling) with explicit enum constraints. A validation layer will reject and retry if the LLM returns out-of-schema tags.
- **Privacy (demographics)**: Only extract what customers explicitly mention. Add a `confidence` score and only surface high-confidence extractions. No inference from external data.
- **Cost**: GPT-4o-mini is cheap (~$0.15/1M input tokens). Embeddings are ~$0.02/1M tokens. At 10K tickets, total LLM cost is under $5.
- **Search quality (rev1)**: Pure vector similarity is a solid starting point. Rev2 adds hybrid search for better precision.
