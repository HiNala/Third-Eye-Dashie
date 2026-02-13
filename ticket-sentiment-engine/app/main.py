"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ingest, search, tickets
from app.db.session import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Skip DB init when running under pytest (tests manage their own DB setup)
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
            )
            await conn.run_sync(Base.metadata.create_all)
    yield
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        await engine.dispose()


app = FastAPI(
    title="Ticket Sentiment Engine",
    description="AI-powered ticket sentiment analysis and demographic extraction API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the frontend dashboard to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(tickets.router, prefix="/api/v1", tags=["tickets"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
