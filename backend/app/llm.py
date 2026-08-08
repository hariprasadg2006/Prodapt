"""
LLM module — all Gemini API interactions.

Provides three high-level functions:
  • summarize_text()
  • extract_insights()
  • answer_question()
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY


def _get_client() -> genai.Client:
    """Return a configured Gemini client."""
    return genai.Client(api_key=GEMINI_API_KEY)


MODEL_ID = "gemini-2.0-flash"


# ── Summarization ──────────────────────────────────────────────────────────

def summarize_text(text: str, filename: str = "document") -> str:
    """
    Generate a concise 150-250 word summary of the given text using Gemini.
    """
    client = _get_client()

    prompt = (
        f"You are a research assistant. Summarize the following document "
        f"('{filename}') in 150-250 words. Use clear, plain language. "
        f"Focus on the key points, findings, and conclusions.\n\n"
        f"--- DOCUMENT TEXT ---\n{text[:30000]}\n--- END ---\n\n"
        f"Summary:"
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=512,
        ),
    )

    return response.text.strip()


def summarize_cross_document(summaries: List[Dict[str, str]]) -> str:
    """
    Generate a cross-document summary from individual document summaries.
    """
    client = _get_client()

    docs_block = "\n\n".join(
        f"[{s['filename']}]: {s['summary']}" for s in summaries
    )

    prompt = (
        "You are a research assistant. Below are summaries of multiple documents. "
        "Write a concise cross-document summary (150-250 words) that highlights "
        "common themes, key differences, and overall takeaways.\n\n"
        f"{docs_block}\n\n"
        "Cross-document summary:"
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=512,
        ),
    )

    return response.text.strip()


# ── Insights extraction ────────────────────────────────────────────────────

def extract_insights(text: str, filename: str = "document") -> List[Dict[str, Any]]:
    """
    Extract 5-8 key insights as structured data with page references.

    Returns a list of dicts: [{"text": "...", "page": int|null}, ...]
    """
    client = _get_client()

    prompt = (
        f"You are a research assistant. Extract 5-8 key insights from the "
        f"following document ('{filename}'). For each insight, provide:\n"
        f"- The insight text (1-2 sentences)\n"
        f"- The approximate source page number if you can infer it from context "
        f"(otherwise null)\n\n"
        f"Return ONLY a valid JSON array in this format:\n"
        f'[{{"text": "insight text", "page": 1}}, ...]\n\n'
        f"--- DOCUMENT TEXT ---\n{text[:30000]}\n--- END ---\n\n"
        f"JSON:"
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )

    # Parse the JSON response
    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first and last lines (code fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    try:
        insights = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return the raw text as a single insight
        insights = [{"text": raw, "page": None}]

    return insights


# ── Q&A with citations ─────────────────────────────────────────────────────

def answer_question(
    question: str,
    context_chunks: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Answer a question using retrieved context chunks, citing [filename, page]
    inline for every claim.

    Returns the answer string.
    """
    client = _get_client()

    # Build context block
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        page_info = f"page {chunk['page']}" if chunk.get("page") else "unknown page"
        context_parts.append(
            f"[Source {i}: {chunk['filename']}, {page_info}]\n{chunk['text']}"
        )
    context_block = "\n\n".join(context_parts)

    # Build chat history block
    history_block = ""
    if chat_history:
        history_lines = []
        for msg in chat_history:
            history_lines.append(f"User: {msg.get('question', '')}")
            history_lines.append(f"Assistant: {msg.get('answer', '')}")
        history_block = (
            "--- PREVIOUS CONVERSATION ---\n"
            + "\n".join(history_lines)
            + "\n--- END PREVIOUS CONVERSATION ---\n\n"
        )

    prompt = (
        "You are a research assistant. Answer the user's question ONLY using "
        "the provided context from uploaded documents. For every claim, cite "
        "the source inline as [filename, page X]. If you cannot find the answer "
        "in the provided context, say: \"I couldn't find information about that "
        "in the uploaded documents.\"\n\n"
        f"{history_block}"
        f"--- CONTEXT ---\n{context_block}\n--- END CONTEXT ---\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )

    return response.text.strip()
