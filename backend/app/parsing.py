"""
Document parsing — extract text from PDF, DOCX, and TXT files.
Returns per-page text where available (PDF), or a single-page list otherwise.
"""

from __future__ import annotations

import io
from typing import List, Tuple


def parse_pdf(file_bytes: bytes) -> Tuple[List[str], int]:
    """
    Extract text from a PDF file.

    Returns:
        (pages, page_count) — a list of text strings (one per page) and total page count.

    Raises:
        ValueError on password-protected or unreadable PDFs.
    """
    import pdfplumber

    pages: List[str] = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF: {exc}") from exc

    if not pages or all(p.strip() == "" for p in pages):
        raise ValueError("PDF appears to be empty or contains no extractable text.")

    return pages, len(pages)


def parse_docx(file_bytes: bytes) -> Tuple[List[str], int]:
    """
    Extract text from a DOCX file.

    Returns:
        ([full_text], 1) — DOCX has no native page concept, so we return all
        text as a single "page".
    """
    from docx import Document

    try:
        doc = Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(f"Failed to parse DOCX: {exc}") from exc

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)

    if not full_text.strip():
        raise ValueError("DOCX appears to be empty.")

    return [full_text], 1


def parse_txt(file_bytes: bytes) -> Tuple[List[str], int]:
    """
    Extract text from a plain-text file.

    Returns:
        ([full_text], 1)
    """
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except Exception as exc:
            raise ValueError(f"Failed to decode TXT file: {exc}") from exc

    if not text.strip():
        raise ValueError("TXT file is empty.")

    return [text], 1


# ── Dispatcher ──────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def parse_file(filename: str, file_bytes: bytes) -> Tuple[List[str], int]:
    """
    Route a file to the correct parser based on extension.

    Returns:
        (pages, page_count)

    Raises:
        ValueError for unsupported types or parsing errors.
    """
    ext = _get_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext == ".docx":
        return parse_docx(file_bytes)
    else:
        return parse_txt(file_bytes)


def _get_extension(filename: str) -> str:
    """Return the lowercased file extension (including the dot)."""
    import os
    _, ext = os.path.splitext(filename)
    return ext.lower()
