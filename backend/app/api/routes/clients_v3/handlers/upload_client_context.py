"""POST /api/v1/clients/{client_id}/upload-context · multipart file upload.

Persiste doc contexto del cliente (PDF/DOCX/MD/TXT · cap 50K chars).
Re-upload sobrescribe (V1 sin history · 1 doc por cliente).
Texto extraído se inyecta SIEMPRE al system prompt de RAFA (diferente
de DEBT-CL-020 que era per-request · este es persistent context).

Reusa _attachment_extractor.extract_text (DEBT-CL-020 · pypdf +
python-docx + utf-8 decode · cap 5MB raw + 50K chars output).
"""
import base64
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, UploadFile, File

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.content_lab_v3._attachment_extractor import (
    ExtractionError, extract_text,
)
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.post("/{client_id}/upload-context")
async def upload_client_context(
    client_id: str,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="client_access_denied")

    raw = await file.read()
    mime = file.content_type or "application/octet-stream"
    b64 = base64.b64encode(raw).decode("ascii")
    try:
        extracted = extract_text(b64, mime)
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=f"extract_failed:{e}")
    if not extracted:
        raise HTTPException(status_code=400, detail="empty_extracted_text")

    sb = get_supabase_service().client
    sb.table("client_context").upsert({
        "client_id": client_id,
        "uploaded_context_text": extracted,
        "uploaded_context_filename": file.filename or "unknown",
        "uploaded_context_mime": mime,
        "uploaded_context_at": datetime.now(timezone.utc).isoformat(),
    }, on_conflict="client_id").execute()

    return {
        "filename": file.filename, "mime": mime,
        "char_count": len(extracted),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
