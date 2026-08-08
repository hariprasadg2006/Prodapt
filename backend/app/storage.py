"""
In-memory session store.

Structure per session:
    sessions[session_id] = {
        "documents": {
            doc_id: {
                "filename": str,
                "page_count": int,
                "full_text": str,          # concatenated raw text
                "pages": [str, ...],       # text per page (for PDFs)
            }
        },
        "chunks": [
            {
                "doc_id": str,
                "filename": str,
                "text": str,
                "page": int | None,
                "embedding": np.ndarray,
            },
            ...
        ]
    }
"""

from __future__ import annotations

from typing import Any, Dict

# Global in-memory store
sessions: Dict[str, Dict[str, Any]] = {}


def create_session(session_id: str) -> Dict[str, Any]:
    """Create a new empty session."""
    sessions[session_id] = {
        "documents": {},
        "chunks": [],
    }
    return sessions[session_id]


def get_session(session_id: str) -> Dict[str, Any] | None:
    """Return the session dict or None if not found."""
    return sessions.get(session_id)
