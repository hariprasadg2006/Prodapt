"""
Pydantic request/response schemas — the data contract for the frontend team.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Upload ──────────────────────────────────────────────────────────────────

class DocumentStatus(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    status: str  # "ok" | error message


class UploadResponse(BaseModel):
    session_id: str
    documents: List[DocumentStatus]


# ── Summary ─────────────────────────────────────────────────────────────────

class SummaryRequest(BaseModel):
    session_id: str
    doc_id: Optional[str] = None


class DocumentSummary(BaseModel):
    doc_id: str
    filename: str
    summary: str


class SummaryResponse(BaseModel):
    summaries: List[DocumentSummary]
    cross_document_summary: Optional[str] = None


# ── Insights ────────────────────────────────────────────────────────────────

class InsightsRequest(BaseModel):
    session_id: str
    doc_id: Optional[str] = None


class Insight(BaseModel):
    text: str
    page: Optional[int] = None


class DocumentInsights(BaseModel):
    doc_id: str
    insights: List[Insight]


class InsightsResponse(BaseModel):
    documents: List[DocumentInsights]


# ── Chat ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    question: str
    answer: str


class ChatRequest(BaseModel):
    session_id: str
    question: str
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)


class Source(BaseModel):
    filename: str
    page: Optional[int] = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


# ── Session info ────────────────────────────────────────────────────────────

class SessionDocument(BaseModel):
    doc_id: str
    filename: str
    page_count: int


class SessionInfoResponse(BaseModel):
    session_id: str
    documents: List[SessionDocument]


# ── Health ──────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"


# ── Error ───────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
