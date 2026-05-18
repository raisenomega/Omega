"""Handler: POST upload hero media for reseller branding"""
import logging
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

_ALLOWED_TYPES = [
    "video/mp4", "video/webm",
    "image/jpeg", "image/png", "image/webp",
]
_MAX_SIZE_MB = 15


async def handle_upload_hero_media(service, reseller: dict, reseller_id: str, file: UploadFile) -> dict:
    """Validate, upload, and link hero media. Returns public URL + media_type."""
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(_ALLOWED_TYPES)}",
        )

    file_data = await file.read()
    file_size_mb = len(file_data) / (1024 * 1024)
    if file_size_mb > _MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size_mb:.2f}MB). Max {_MAX_SIZE_MB}MB allowed.",
        )

    media_type = "video" if file.content_type.startswith("video/") else "image"
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
    file_path = f"{reseller['slug']}/hero.{file_extension}"

    public_url = await service.upload_media(
        bucket="reseller-media",
        file_path=file_path,
        file_data=file_data,
        content_type=file.content_type,
    )

    await service.update_branding(reseller_id, {
        "hero_media_url": public_url,
        "hero_media_type": media_type,
    })

    return {"url": public_url, "media_type": media_type}
