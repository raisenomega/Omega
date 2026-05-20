"""POST /api/v1/clients/{client_id}/brand-files · upload a Supabase Storage.

DDD A1/A9: handler → infrastructure helper · sin Supabase directo.
Bucket 'brand-files' debe existir (DEBT-041 · config Storage pendiente).
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Form
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3._clients_repository import _sb

router = APIRouter()

ALLOWED_CATEGORIES = {"logo", "brand_guide", "sample_content", "other"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/{client_id}/brand-files")
async def upload_brand_file(
    client_id: str,
    file: UploadFile = File(...),
    file_category: str = Form(...),
    authorization: Optional[str] = Header(None),
) -> dict:
    await get_current_user(authorization)
    if file_category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=422, detail="invalid_file_category")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file_too_large")
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "bin"
    path = f"{client_id}/{uuid.uuid4()}.{ext}"
    try:
        _sb().storage.from_("brand-files").upload(path, content, {"content-type": file.content_type or "application/octet-stream"})
        url = _sb().storage.from_("brand-files").get_public_url(path)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"storage_unavailable:{type(e).__name__}")
    r = _sb().table("brand_files").insert({
        "client_id": client_id, "filename": file.filename, "storage_path": path,
        "file_type": ext, "size_bytes": len(content), "mime_type": file.content_type,
        "storage_url": url, "file_category": file_category,
    }).execute()
    return {"id": r.data[0]["id"], "storage_url": url, "file_category": file_category}
