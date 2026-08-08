"""
AI Research Assistant — FastAPI Backend

Entry point: registers all routers, enables CORS, validates config on startup.
"""

import os
# Must be set BEFORE any transformers import to prevent Keras 3 / TensorFlow conflict
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import validate_config
from app.models import HealthResponse, SessionInfoResponse, SessionDocument
from app.storage import get_session

from app.routes.upload import router as upload_router
from app.routes.summary import router as summary_router
from app.routes.insights import router as insights_router
from app.routes.chat import router as chat_router

logger = logging.getLogger("uvicorn.error")


# ── Startup / shutdown ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate configuration on startup."""
    validate_config()
    logger.info("✅ GEMINI_API_KEY is set — server is ready.")
    yield
    logger.info("Server shutting down.")


# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Research Assistant",
    description="Upload documents, get summaries, extract insights, and ask questions with citations.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins (demo only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────

app.include_router(upload_router, tags=["Upload"])
app.include_router(summary_router, tags=["Summary"])
app.include_router(insights_router, tags=["Insights"])
app.include_router(chat_router, tags=["Chat"])


# ── Utility endpoints ─────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Utility"])
async def health():
    """Health check."""
    return HealthResponse(status="ok")


@app.get(
    "/session/{session_id}",
    response_model=SessionInfoResponse,
    tags=["Utility"],
)
async def session_info(session_id: str):
    """List documents in a session (for frontend to rehydrate state on refresh)."""
    session = get_session(session_id)
    if session is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found.")

    docs = [
        SessionDocument(
            doc_id=doc_id,
            filename=doc["filename"],
            page_count=doc["page_count"],
        )
        for doc_id, doc in session["documents"].items()
    ]

    return SessionInfoResponse(session_id=session_id, documents=docs)
