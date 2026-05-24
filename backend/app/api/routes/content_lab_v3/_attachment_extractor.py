"""Attachment text extractor · DEBT-CL-020 + sanitización (SPRINT 4A-3 #1).

input (b64, mime) → texto extraído y SANITIZADO (input_sanitizer · contexto
UPLOADED_DOCUMENT, T2) o None (imágenes · caller usa b64 como referencia visual).
Branches MIME: image/* → None · pdf → pypdf · docx → python-docx · text/* → utf-8.
Cap raw 5MB. Doc no confiable (BLOCK/HOLD/fail-closed del sanitizer) → ExtractionError.
"""
from __future__ import annotations

import base64
import io
import logging
from typing import Optional

from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction

logger = logging.getLogger(__name__)

MAX_RAW_BYTES = 5 * 1024 * 1024  # 5MB
MAX_OUTPUT_CHARS = 50_000  # bound pre-sanitize · el cap final (20K) lo aplica input_sanitizer
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ExtractionError(Exception):
    """Falla de extracción o de seguridad · handler la mapea a HTTPException 400/422."""


def extract_text(b64: str, mime_type: str) -> Optional[str]:
    """Decode base64 + extract + sanitiza (T2). Retorna None para imágenes."""
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
        text = _extract_pdf(raw)
    elif mime_type == _DOCX_MIME or mime_type.endswith("wordprocessingml.document"):
        text = _extract_docx(raw)
    elif mime_type.startswith("text/"):
        text = _extract_plain(raw)
    else:
        raise ExtractionError(f"unsupported_mime:{mime_type}")
    return _sanitize(text)


def _sanitize(text: str) -> str:
    """Sanitiza doc no confiable (T2). BLOCK/HOLD/fail-closed → ExtractionError."""
    out, err = sanitize_input(text, InputContext.UPLOADED_DOCUMENT)
    if err is not None:
        raise ExtractionError(f"sanitizer_failure:{err.code}")
    if out.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        raise ExtractionError(f"unsafe_attachment:{out.action.value}")
    return out.clean_text


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
