"""Upload handler and constants for brand files"""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import HTTPException, UploadFile

from app.infrastructure.supabase_service import get_supabase_service
from .models import BrandFileProfile, BrandFileResponse

logger = logging.getLogger(__name__)

PLAN_LIMITS = {
    "basic": {"max_files": 3, "max_size_mb": 10, "total_mb": 25},
    "pro": {"max_files": 10, "max_size_mb": 25, "total_mb": 100},
    "enterprise": {"max_files": 30, "max_size_mb": 50, "total_mb": 500},
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/png",
    "image/jpeg",
    "image/webp",
}


async def handle_upload_brand_file(
    client_id: str, file: UploadFile
) -> BrandFileResponse:
    """Validate plan limits, upload to Supabase Storage, save record."""
    supabase = get_supabase_service()

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}",
        )

    client_result = supabase.client.table("clients")\
        .select("plan")\
        .eq("id", client_id)\
        .single()\
        .execute()

    if not client_result.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    plan = client_result.data.get("plan", "basic")
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["basic"])

    existing = supabase.client.table("brand_files")\
        .select("file_size")\
        .eq("client_id", client_id)\
        .execute()

    existing_files = existing.data or []
    existing_count = len(existing_files)
    existing_total_mb = sum(f.get("file_size", 0) for f in existing_files) / (1024 * 1024)

    if existing_count >= limits["max_files"]:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Límite alcanzado. Plan {plan.capitalize()} permite "
                f"{limits['max_files']} archivos. Actualiza tu plan para más espacio."
            ),
        )

    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)

    if file_size_mb > limits["max_size_mb"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Archivo muy grande ({file_size_mb:.1f}MB). "
                f"Máximo {limits['max_size_mb']}MB por archivo en plan {plan.capitalize()}."
            ),
        )

    if existing_total_mb + file_size_mb > limits["total_mb"]:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Espacio insuficiente. Plan {plan.capitalize()} tiene "
                f"{limits['total_mb']}MB total. Usando {existing_total_mb:.1f}MB. "
                f"Actualiza tu plan."
            ),
        )

    file_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    storage_path = f"{client_id}/{file_id}.{file_ext}"

    supabase.client.storage\
        .from_("brand-guides")\
        .upload(storage_path, file_content, {"content-type": file.content_type})

    url_result = supabase.client.storage\
        .from_("brand-guides")\
        .get_public_url(storage_path)

    db_result = supabase.client.table("brand_files").insert({
        "client_id": client_id,
        "file_name": file.filename,
        "file_path": storage_path,
        "file_size": len(file_content),
        "mime_type": file.content_type,
        "storage_url": url_result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    if not db_result.data:
        raise HTTPException(status_code=500, detail="Error guardando referencia del archivo")

    logger.info(f"Brand file uploaded: {file.filename} for client {client_id} ({file_size_mb:.1f}MB)")

    return BrandFileResponse(
        success=True,
        data=BrandFileProfile(**db_result.data[0]),
        message=f"Archivo {file.filename} subido exitosamente",
    )
