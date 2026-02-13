"""FastAPI application entry point."""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ingest, search, tickets
from app.config import settings
from app.db.base import Base
from app.db.session import engine
from app.logging_config import setup_logging

# Initialize logging before anything else
setup_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("Ticket Sentiment Engine starting up")
    logger.info("LLM provider: %s (model: %s)", settings.llm_provider.value, settings.llm_model)
    logger.info("Embedding provider: %s (model: %s)", settings.embedding_provider.value, settings.embedding_model)
    logger.info("Database: %s", settings.database_url.split("@")[-1])  # hide credentials
    logger.info("=" * 60)

    # Skip DB init when running under pytest (tests manage their own DB setup)
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        logger.info("Initializing database schema...")
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
            )
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema ready")
    else:
        logger.info("Running under pytest — skipping DB init")

    yield

    logger.info("Shutting down...")
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        await engine.dispose()
    logger.info("Shutdown complete")


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


# ---------- Request logging middleware ----------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response time."""
    start = time.perf_counter()
    request_id = request.headers.get("x-request-id", "-")

    logger.info(
        ">>> %s %s (request_id=%s)",
        request.method,
        request.url.path,
        request_id,
    )

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "<<< %s %s -> %d (%.1fms, request_id=%s)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response


# Register route modules
app.include_router(tickets.router, prefix="/api/v1", tags=["tickets"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
