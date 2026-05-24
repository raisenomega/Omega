"""Attachment text extractor · DEBT-CL-020.

Capa puente entre handler y libs externas (pypdf · python-docx). Función
pública pura desde la perspectiva del handler: input (b64, mime) → output
texto extraído o None (caso imagen · caller usa b64 como referencia visual).

Branches por MIME:
- image/*                                          → None (no text extract)
- application/pdf                                  → pypdf · cap 50K chars
- application/vnd.openxmlformats-...wordprocessingml.document → python-docx · cap 50K
- text/* (markdown, plain, csv, etc.)              → decode utf-8 · cap 50K
- otros                                            → ExtractionError

Cap 5MB raw (frontend ya valida · defense in depth server-side).
Cap 50K chars output (~12K tokens · cabe en contexto Claude).
"""
from __future__ import annotations

import base64
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

MAX_RAW_BYTES = 5 * 1024 * 1024  # 5MB
MAX_OUTPUT_CHARS = 50_000
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ExtractionError(Exception):
    """Falla de extracción · handler la mapea a HTTPException 400/422."""


def extract_text(b64: str, mime_type: str) -> Optional[str]:
    """Decode base64 + extract text según mime. Retorna None para imágenes."""
    if not b64 or not mime_type:
        return None
    if mime_type.startswith("image/"):
        return None
    try:
        raw = base64.b64decode(b64, validate=False)
    except Exception as e:
        raise ExtractionError(f"invalid_base64:{type(e).__name__}")
    if len(raw) > MAX_RAW_BYTES:
        raise ExtractionError(f"attachment_too_large:{len(raw)}>5MB")

    if mime_type == "application/pdf":
        return _extract_pdf(raw)
    if mime_type == _DOCX_MIME or mime_type.endswith("wordprocessingml.document"):
        return _extract_docx(raw)
    if mime_type.startswith("text/"):
        return _extract_plain(raw)
    raise ExtractionError(f"unsupported_mime:{mime_type}")


def _extract_pdf(raw: bytes) -> str:
    from pypdf import PdfReader  # lazy import
    try:
        pdf = PdfReader(io.BytesIO(raw))
        parts = [p.extract_text() or "" for p in pdf.pages]
        text = "\n".join(parts).strip()
    except Exception as e:
        logger.error(f"pdf extract failed: {e}", exc_info=True)
        raise ExtractionError(f"pdf_extract_failed:{type(e).__name__}")
    if not text:
        raise ExtractionError("pdf_empty")
    return text[:MAX_OUTPUT_CHARS]


def _extract_docx(raw: bytes) -> str:
    from docx import Document  # lazy import
    try:
        doc = Document(io.BytesIO(raw))
        text = "\n".join(p.text for p in doc.paragraphs if p.text).strip()
    except Exception as e:
        logger.error(f"docx extract failed: {e}", exc_info=True)
        raise ExtractionError(f"docx_extract_failed:{type(e).__name__}")
    if not text:
        raise ExtractionError("docx_empty")
    return text[:MAX_OUTPUT_CHARS]


def _extract_plain(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore").strip()
    if not text:
        raise ExtractionError("text_empty")
    return text[:MAX_OUTPUT_CHARS]
