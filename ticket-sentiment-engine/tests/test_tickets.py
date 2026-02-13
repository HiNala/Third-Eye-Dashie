"""Unit tests for Pydantic schemas and ticket validation."""

import uuid
from datetime import datetime, timezone

import pytest

from app.schemas.ticket import (
    IngestRequest,
    ProcessingStatus,
    SearchRequest,
    TagItem,
    TicketIngestItem,
    TicketResponse,
    TicketStatus,
    UpdateStatusRequest,
    UpdateTagsRequest,
)


def test_ticket_response_from_dict():
    """TicketResponse can be built from a dict (simulating joined raw+processed output)."""
    data = {
        "id": uuid.uuid4(),
        "title": "Test ticket",
        "content": "Content here",
        "tags": [{"category": "sentiment", "value": "positive"}],
        "demographics": None,
        "sentiment": "positive",
        "emotional_tone": "happy",
        "confidence": 0.95,
        "customer_email": "test@example.com",
        "status": "open",
        "processing_status": "completed",
        "created_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc),
    }
    ticket = TicketResponse(**data)
    assert ticket.title == "Test ticket"
    assert ticket.sentiment.value == "positive"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.processing_status == ProcessingStatus.COMPLETED


def test_ticket_response_pending_processing():
    """TicketResponse defaults to pending processing status."""
    data = {
        "id": uuid.uuid4(),
        "title": "Unprocessed ticket",
        "content": "Content here",
        "customer_email": "test@example.com",
        "status": "open",
        "created_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc),
    }
    ticket = TicketResponse(**data)
    assert ticket.processing_status == ProcessingStatus.PENDING
    assert ticket.sentiment is None
    assert ticket.tags is None


def test_ticket_status_enum():
    """TicketStatus enum contains expected values."""
    assert TicketStatus.OPEN == "open"
    assert TicketStatus.IN_PROGRESS == "in_progress"
    assert TicketStatus.CLOSED == "closed"


def test_update_status_valid():
    """UpdateStatusRequest accepts valid statuses."""
    for status in ["open", "in_progress", "closed"]:
        req = UpdateStatusRequest(status=status)
        assert req.status.value == status


def test_update_status_invalid():
    """UpdateStatusRequest rejects invalid statuses."""
    with pytest.raises(ValueError):
        UpdateStatusRequest(status="banana")


def test_update_tags_request():
    """UpdateTagsRequest parses tag items."""
    req = UpdateTagsRequest(tags=[
        {"category": "sentiment", "value": "negative"},
        {"category": "priority", "value": "urgent"},
    ])
    assert len(req.tags) == 2
    assert req.tags[0].category == "sentiment"


def test_ingest_request():
    """IngestRequest parses a batch of tickets."""
    req = IngestRequest(tickets=[
        {
            "title": "Ticket 1",
            "content": "Content 1",
            "customer_email": "a@test.com",
        },
        {
            "title": "Ticket 2",
            "content": "Content 2",
            "customer_email": "b@test.com",
            "status": "in_progress",
        },
    ])
    assert len(req.tickets) == 2
    assert req.tickets[0].status == TicketStatus.OPEN  # default
    assert req.tickets[1].status == TicketStatus.IN_PROGRESS


def test_ingest_item_default_status():
    """TicketIngestItem defaults to 'open' status."""
    item = TicketIngestItem(
        title="Test",
        content="Content",
        customer_email="test@test.com",
    )
    assert item.status == TicketStatus.OPEN


def test_ingest_missing_required_field():
    """TicketIngestItem requires title, content, customer_email."""
    with pytest.raises(ValueError):
        TicketIngestItem(title="Test", content="Content")  # missing email


def test_search_request_defaults():
    """SearchRequest has sensible defaults."""
    req = SearchRequest(query="shipping issues")
    assert req.limit == 10


def test_search_request_limit_bounds():
    """SearchRequest limit must be 1-100."""
    with pytest.raises(ValueError):
        SearchRequest(query="test", limit=0)
    with pytest.raises(ValueError):
        SearchRequest(query="test", limit=101)


def test_tag_item():
    """TagItem holds category and value."""
    tag = TagItem(category="sentiment", value="positive")
    assert tag.category == "sentiment"
    assert tag.model_dump() == {"category": "sentiment", "value": "positive"}
