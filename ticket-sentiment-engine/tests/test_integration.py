"""Integration tests — hit the running Docker app with real HTTP calls.

Run these with: pytest tests/test_integration.py -v
Requires: docker compose up (app + db running on localhost:8000)
"""

import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _ingest_ticket(title: str, content: str, email: str = "integration@test.com"):
    """Helper to ingest a single ticket and return its ID."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        resp = await c.post("/api/v1/ingest", json={
            "tickets": [{
                "title": title,
                "content": content,
                "customer_email": email,
                "status": "open",
            }]
        })
        resp.raise_for_status()
        return resp.json()["ticket_ids"][0]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_health_check():
    """App health endpoint responds."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as c:
        resp = await c.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


async def test_openapi_docs():
    """Swagger docs are accessible."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as c:
        resp = await c.get("/docs")
        assert resp.status_code == 200


async def test_ingest_and_retrieve():
    """Full flow: ingest a ticket, then retrieve it by ID."""
    ticket_id = await _ingest_ticket(
        title="Integration test ticket",
        content="This ticket was created by an integration test.",
    )

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        resp = await c.get(f"/api/v1/tickets/{ticket_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Integration test ticket"
        assert data["customer_email"] == "integration@test.com"
        assert data["status"] == "open"


async def test_get_all_tickets():
    """GET /tickets returns a list with count."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        resp = await c.get("/api/v1/tickets")
        assert resp.status_code == 200
        data = resp.json()
        assert "tickets" in data
        assert "count" in data
        assert isinstance(data["tickets"], list)
        assert data["count"] >= 0


async def test_update_tags():
    """Update tags on a ticket and verify."""
    ticket_id = await _ingest_ticket(
        title="Tag update integration test",
        content="Ticket for testing tag updates.",
    )

    new_tags = [
        {"category": "sentiment", "value": "positive"},
        {"category": "priority", "value": "high"},
    ]

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        resp = await c.post(
            f"/api/v1/tickets/{ticket_id}/tags",
            json={"tags": new_tags},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tags"]) == 2
        tag_categories = {t["category"] for t in data["tags"]}
        assert "sentiment" in tag_categories
        assert "priority" in tag_categories


async def test_update_status_lifecycle():
    """Walk a ticket through open -> in_progress -> closed."""
    ticket_id = await _ingest_ticket(
        title="Status lifecycle test",
        content="Test the full status lifecycle.",
    )

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        # open -> in_progress
        resp = await c.post(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "in_progress"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

        # in_progress -> closed
        resp = await c.post(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "closed"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "closed"


async def test_get_nonexistent_ticket():
    """GET for a random UUID returns 404."""
    fake_id = str(uuid.uuid4())
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as c:
        resp = await c.get(f"/api/v1/tickets/{fake_id}")
        assert resp.status_code == 404


async def test_search_endpoint_exists():
    """POST /tickets/search endpoint is reachable (may fail without embedding service)."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        resp = await c.post(
            "/api/v1/tickets/search",
            json={"query": "shipping issues", "limit": 5},
        )
        # 200 if embeddings are configured, 502 if not — both are acceptable
        assert resp.status_code in (200, 502)
