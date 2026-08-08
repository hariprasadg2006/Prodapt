"""
POST /insights — key insights extraction endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import (
    DocumentInsights,
    Insight,
    InsightsRequest,
    InsightsResponse,
)
from app.storage import get_session
from app.llm import extract_insights

router = APIRouter()


@router.post("/insights", response_model=InsightsResponse)
async def get_insights(req: InsightsRequest):
    """
    Extract 5-8 key insights from one document or all documents.
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

        raw_insights = extract_insights(doc["full_text"], doc["filename"])
        insights = [
            Insight(text=ins.get("text", ""), page=ins.get("page"))
            for ins in raw_insights
        ]
        return InsightsResponse(
            documents=[
                DocumentInsights(doc_id=req.doc_id, insights=insights)
            ]
        )

    # Extract insights from all documents
    all_doc_insights = []
    for doc_id, doc in documents.items():
        raw_insights = extract_insights(doc["full_text"], doc["filename"])
        insights = [
            Insight(text=ins.get("text", ""), page=ins.get("page"))
            for ins in raw_insights
        ]
        all_doc_insights.append(
            DocumentInsights(doc_id=doc_id, insights=insights)
        )

    return InsightsResponse(documents=all_doc_insights)
