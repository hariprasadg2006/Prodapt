"""
POST /summary — document summarization endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import (
    DocumentSummary,
    SummaryRequest,
    SummaryResponse,
)
from app.storage import get_session
from app.llm import summarize_text, summarize_cross_document

router = APIRouter()


@router.post("/summary", response_model=SummaryResponse)
async def get_summary(req: SummaryRequest):
    """
    Summarize one document (if doc_id provided) or all documents in the session.
    When 2+ docs exist and no doc_id is specified, also returns a cross-document summary.
    """
    session = get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    documents = session["documents"]
    if not documents:
        raise HTTPException(status_code=404, detail="No documents in this session.")

    # If a specific doc_id is requested
    if req.doc_id:
        doc = documents.get(req.doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail=f"Document '{req.doc_id}' not found.")

        summary_text = summarize_text(doc["full_text"], doc["filename"])
        return SummaryResponse(
            summaries=[
                DocumentSummary(
                    doc_id=req.doc_id,
                    filename=doc["filename"],
                    summary=summary_text,
                )
            ],
            cross_document_summary=None,
        )

    # Summarize all documents
    summaries = []
    for doc_id, doc in documents.items():
        summary_text = summarize_text(doc["full_text"], doc["filename"])
        summaries.append(
            DocumentSummary(
                doc_id=doc_id,
                filename=doc["filename"],
                summary=summary_text,
            )
        )

    # Cross-document summary if 2+ docs
    cross_summary = None
    if len(summaries) >= 2:
        cross_summary = summarize_cross_document(
            [{"filename": s.filename, "summary": s.summary} for s in summaries]
        )

    return SummaryResponse(
        summaries=summaries,
        cross_document_summary=cross_summary,
    )
