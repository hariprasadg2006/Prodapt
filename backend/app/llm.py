"""
LLM module — supports OpenRouter (OpenAI-compatible) and Google Gemini API.

Provides three high-level functions:
  • summarize_text()
  • extract_insights()
  • answer_question()
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import httpx

from app.config import GEMINI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_MODEL

GEMINI_MODEL_ID = "gemini-2.0-flash"


def _generate(prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
    """Generate completion using OpenRouter if available, falling back to Gemini."""
    if OPENROUTER_API_KEY:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    else:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text.strip()


# ── Summarization ──────────────────────────────────────────────────────────

def summarize_text(text: str, filename: str = "document") -> str:
    """
    Generate a concise 150-250 word summary of the given text.
    """
    prompt = (
        f"You are a research assistant. Summarize the following document "
        f"('{filename}') in 150-250 words. Use clear, plain language. "
        f"Focus on the key points, findings, and conclusions.\n\n"
        f"--- DOCUMENT TEXT ---\n{text[:30000]}\n--- END ---\n\n"
        f"Summary:"
    )

    return _generate(prompt, max_tokens=512, temperature=0.3)


def summarize_cross_document(summaries: List[Dict[str, str]]) -> str:
    """
    Generate a cross-document summary from individual document summaries.
    """
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

    return _generate(prompt, max_tokens=512, temperature=0.3)


# ── Insights extraction ────────────────────────────────────────────────────

def extract_insights(text: str, filename: str = "document") -> List[Dict[str, Any]]:
    """
    Extract 5-8 key insights as structured data with page references.

    Returns a list of dicts: [{"text": "...", "page": int|null}, ...]
    """
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

    raw = _generate(prompt, max_tokens=1024, temperature=0.3)

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines)

    try:
        insights = json.loads(raw)
    except json.JSONDecodeError:
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
    """
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        page_info = f"page {chunk['page']}" if chunk.get("page") else "unknown page"
        context_parts.append(
            f"[Source {i}: {chunk['filename']}, {page_info}]\n{chunk['text']}"
        )
    context_block = "\n\n".join(context_parts)

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

    return _generate(prompt, max_tokens=1024, temperature=0.3)
