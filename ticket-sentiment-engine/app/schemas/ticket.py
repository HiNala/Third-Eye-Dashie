"""Pydantic schemas for ticket API request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


# ---------- Enums ----------

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class SentimentValue(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EmotionalToneValue(str, Enum):
    ANGRY = "angry"
    HAPPY = "happy"
    FRUSTRATED = "frustrated"
    DELIGHTED = "delighted"
    NEUTRAL = "neutral"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


# ---------- Tag ----------

class TagItem(BaseModel):
    category: str
    value: str


# ---------- Demographic ----------

class DemographicField(BaseModel):
    value: str | None = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class Demographics(BaseModel):
    family_status: DemographicField | None = None
    health_conditions: DemographicField | None = None
    location: DemographicField | None = None
    occupation: DemographicField | None = None
    age_bracket: DemographicField | None = None


# ---------- Ticket Response (joined view: raw + processed) ----------

class TicketResponse(BaseModel):
    """Combined view of raw ticket data + LLM processing results.

    The `id` is the raw_ticket_id — the stable, canonical identifier.
    Processing fields (sentiment, tags, etc.) are None when not yet processed.
    """

    id: uuid.UUID
    title: str
    content: str
    tags: list[TagItem] | None = None
    demographics: Demographics | None = None
    sentiment: SentimentValue | None = None
    emotional_tone: EmotionalToneValue | None = None
    confidence: float | None = None
    customer_email: str
    status: TicketStatus
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime
    last_updated: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    count: int


# ---------- Ingestion ----------

class TicketIngestItem(BaseModel):
    title: str
    content: str
    customer_email: str
    status: TicketStatus = TicketStatus.OPEN


class IngestRequest(BaseModel):
    tickets: list[TicketIngestItem]


class IngestResponse(BaseModel):
    accepted: bool = True
    ticket_ids: list[uuid.UUID]
    message: str


# ---------- Update endpoints ----------

class UpdateTagsRequest(BaseModel):
    tags: list[TagItem]


class UpdateStatusRequest(BaseModel):
    status: TicketStatus


# ---------- Search ----------

class SearchRequest(BaseModel):
    query: str
    limit: int = Field(10, ge=1, le=100)


class SearchResponse(BaseModel):
    tickets: list[TicketResponse]
    count: int
