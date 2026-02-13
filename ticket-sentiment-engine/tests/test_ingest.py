"""Unit tests for ingestion-related schemas and validation."""

import pytest

from app.schemas.ticket import IngestRequest, IngestResponse, TicketStatus


def test_ingest_request_single():
    """IngestRequest parses a single ticket."""
    req = IngestRequest(tickets=[{
        "title": "Test",
        "content": "Test content",
        "customer_email": "test@test.com",
    }])
    assert len(req.tickets) == 1
    assert req.tickets[0].status == TicketStatus.OPEN


def test_ingest_request_multiple():
    """IngestRequest parses multiple tickets."""
    req = IngestRequest(tickets=[
        {"title": f"Ticket {i}", "content": f"Content {i}", "customer_email": f"t{i}@test.com"}
        for i in range(5)
    ])
    assert len(req.tickets) == 5


def test_ingest_request_empty():
    """IngestRequest accepts an empty ticket list."""
    req = IngestRequest(tickets=[])
    assert len(req.tickets) == 0


def test_ingest_request_with_status():
    """IngestRequest respects provided status."""
    req = IngestRequest(tickets=[{
        "title": "Test",
        "content": "Test content",
        "customer_email": "test@test.com",
        "status": "in_progress",
    }])
    assert req.tickets[0].status == TicketStatus.IN_PROGRESS


def test_ingest_request_invalid_status():
    """IngestRequest rejects invalid status."""
    with pytest.raises(ValueError):
        IngestRequest(tickets=[{
            "title": "Test",
            "content": "Test content",
            "customer_email": "test@test.com",
            "status": "invalid",
        }])


def test_ingest_request_missing_fields():
    """IngestRequest rejects tickets with missing required fields."""
    with pytest.raises(ValueError):
        IngestRequest(tickets=[{"title": "Test"}])


def test_ingest_response_model():
    """IngestResponse serializes correctly."""
    import uuid
    ids = [uuid.uuid4(), uuid.uuid4()]
    resp = IngestResponse(
        accepted=True,
        ticket_ids=ids,
        message="2 ticket(s) queued for processing",
    )
    assert resp.accepted is True
    assert len(resp.ticket_ids) == 2
    assert "2 ticket(s)" in resp.message
