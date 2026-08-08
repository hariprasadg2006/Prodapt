"""
POST /upload — document ingestion endpoint.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models import DocumentStatus, UploadResponse
from app.parsing import parse_file
from app.chunking import chunk_text, embed_chunks
from app.storage import create_session

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accept multiple files (PDF, DOCX, TXT), parse, chunk, embed,
    and store under a new session_id.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    session_id = str(uuid.uuid4())
    session = create_session(session_id)
    doc_statuses: List[DocumentStatus] = []

    for file in files:
        doc_id = str(uuid.uuid4())
        filename = file.filename or "unnamed"

        try:
            file_bytes = await file.read()
            if not file_bytes:
                raise ValueError("File is empty.")

            # Parse
            pages, page_count = parse_file(filename, file_bytes)
            full_text = "\n".join(pages)

            # Store document metadata
            session["documents"][doc_id] = {
                "filename": filename,
                "page_count": page_count,
                "full_text": full_text,
                "pages": pages,
            }

            # Chunk
            chunks = chunk_text(pages, doc_id, filename)

            # Embed
            chunks = embed_chunks(chunks)

            # Add to session chunk store
            session["chunks"].extend(chunks)

            doc_statuses.append(
                DocumentStatus(
                    doc_id=doc_id,
                    filename=filename,
                    page_count=page_count,
                    status="ok",
                )
            )

        except ValueError as exc:
            # Per-file error — don't crash the batch
            doc_statuses.append(
                DocumentStatus(
                    doc_id=doc_id,
                    filename=filename,
                    page_count=0,
                    status=f"error: {exc}",
                )
            )
        except Exception as exc:
            doc_statuses.append(
                DocumentStatus(
                    doc_id=doc_id,
                    filename=filename,
                    page_count=0,
                    status=f"error: unexpected failure — {exc}",
                )
            )

    return UploadResponse(session_id=session_id, documents=doc_statuses)
