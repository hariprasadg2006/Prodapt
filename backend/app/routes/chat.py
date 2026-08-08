"""
POST /chat — Q&A with citations endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse, Source
from app.storage import get_session
from app.chunking import search_chunks
from app.llm import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Answer a question using RAG: embed the question, retrieve relevant chunks
    via cosine similarity, call Gemini with context, and return the answer
    with source citations.
    """
    session = get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    chunks = session.get("chunks", [])
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No documents have been uploaded to this session yet.",
        )

    # Retrieve relevant chunks
    relevant = search_chunks(query=req.question, chunks=chunks, top_k=6, threshold=0.3)

    # If nothing is relevant enough, return a "can't find" answer
    if not relevant:
        return ChatResponse(
            answer=(
                "I couldn't find information about that in the uploaded documents. "
                "Try rephrasing your question or uploading more relevant documents."
            ),
            sources=[],
        )

    # Build chat history for context
    history = None
    if req.chat_history:
        history = [
            {"question": msg.question, "answer": msg.answer}
            for msg in req.chat_history
        ]

    # Call Gemini
    answer_text = answer_question(
        question=req.question,
        context_chunks=relevant,
        chat_history=history,
    )

    # Build source list
    sources = [
        Source(
            filename=chunk["filename"],
            page=chunk.get("page"),
            snippet=chunk["text"][:200] + ("..." if len(chunk["text"]) > 200 else ""),
        )
        for chunk in relevant
    ]

    return ChatResponse(answer=answer_text, sources=sources)
