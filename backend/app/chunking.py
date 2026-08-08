"""
Text chunking, embedding, and similarity search.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings and numpy
cosine similarity for retrieval — no vector DB needed.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

# Lazy-loaded model singleton
_model = None


def _get_model():
    """Lazy-load the sentence-transformer model (heavy import)."""
    global _model
    if _model is None:
        import os
        os.environ["TF_USE_LEGACY_KERAS"] = "1"
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ── Chunking ────────────────────────────────────────────────────────────────

def chunk_text(
    pages: List[str],
    doc_id: str,
    filename: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """
    Split document text into ~chunk_size-token overlapping chunks.

    Each chunk carries metadata: doc_id, filename, page number (1-indexed).
    Token count is approximated as word count (close enough for a demo).

    Returns a list of chunk dicts (without embeddings yet).
    """
    chunks: List[Dict[str, Any]] = []

    for page_idx, page_text in enumerate(pages):
        page_num = page_idx + 1  # 1-indexed
        words = page_text.split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text_str = " ".join(chunk_words)

            chunks.append({
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk_text_str,
                "page": page_num,
            })

            # Advance by (chunk_size - overlap), minimum 1
            step = max(chunk_size - overlap, 1)
            start += step

    return chunks


# ── Embedding ───────────────────────────────────────────────────────────────

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a list of text strings using all-MiniLM-L6-v2.

    Returns an (N, 384) float32 numpy array.
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    # Ensure we have a numpy array regardless of sentence-transformers version
    if not isinstance(embeddings, np.ndarray):
        import torch
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.cpu().numpy()
        else:
            embeddings = np.array(embeddings)
    return embeddings.astype(np.float32)


def embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compute and attach embeddings to each chunk dict in-place.
    """
    if not chunks:
        return chunks

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    return chunks


# ── Similarity search ──────────────────────────────────────────────────────

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors."""
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(dot / norm)


def search_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 6,
    threshold: float = 0.3,
) -> List[Dict[str, Any]]:
    """
    Embed the query and return the top-k most similar chunks
    (above the similarity threshold).

    Each returned dict includes 'score' alongside the original chunk fields.
    """
    if not chunks:
        return []

    query_emb = embed_texts([query])[0]

    scored: List[tuple] = []
    for chunk in chunks:
        emb = chunk.get("embedding")
        if emb is None:
            continue
        score = cosine_similarity(query_emb, emb)
        if score >= threshold:
            scored.append((score, chunk))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, chunk in scored[:top_k]:
        results.append({
            "doc_id": chunk["doc_id"],
            "filename": chunk["filename"],
            "text": chunk["text"],
            "page": chunk["page"],
            "score": round(score, 4),
        })

    return results
