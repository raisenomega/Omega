"""Storage uploader · bytes → URL pública en Supabase Storage.

Imagen (DEBT-018 · cerrada 22 may) + video (DEBT-019 · cerrada 22 may).
Service role bypasses RLS. Fail-loud: raise StorageUploadError si algo falla
(asset generado sin URL persistido = output inútil · debe abortar el flow).

DEBT-068 (26 may): la subida es I/O de red del cliente Supabase SÍNCRONO → corre
en asyncio.to_thread para NO bloquear el event loop bajo concurrencia. Las
funciones públicas son async; los callers deben await.
"""
import asyncio
import uuid
from typing import Final, Optional

from app.infrastructure.supabase_service import get_supabase_service


_IMAGE_MIME_TO_EXT: Final[dict[str, str]] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
_VIDEO_MIME_TO_EXT: Final[dict[str, str]] = {"video/mp4": "mp4"}

_IMAGES_BUCKET: Final[str] = "generated-images"
_VIDEOS_BUCKET: Final[str] = "generated-videos"


class StorageUploadError(Exception):
    """Falla al subir bytes a Supabase Storage."""


async def _upload_bytes(
    raw: bytes, mime_type: str, bucket: str,
    mime_table: dict[str, str], client_id: Optional[str],
) -> str:
    """Valida MIME + UUID path + upload + retorna URL pública.

    DEBT-068: el upload bloqueante (cliente Supabase sync) corre en un hilo para
    no bloquear el event loop. StorageUploadError se propaga vía asyncio.to_thread.
    """
    ext = mime_table.get(mime_type)
    if not ext:
        raise StorageUploadError(
            f"MIME no soportado para {bucket}: {mime_type!r} · "
            f"permitidos: {sorted(mime_table)}"
        )
    path = f"{client_id or 'shared'}/{uuid.uuid4().hex}.{ext}"

    def _blocking_upload() -> str:
        sb = get_supabase_service().client
        try:
            sb.storage.from_(bucket).upload(
                path=path, file=raw,
                file_options={"content-type": mime_type, "upsert": "false"},
            )
        except Exception as e:
            raise StorageUploadError(
                f"upload failed · client={client_id} bucket={bucket} "
                f"path={path}: {e}"
            ) from e
        return sb.storage.from_(bucket).get_public_url(path)

    return await asyncio.to_thread(_blocking_upload)


async def upload_image_bytes(
    image_bytes: bytes, mime_type: str, client_id: Optional[str] = None,
) -> str:
    """Sube imagen a generated-images/{client_id|shared}/{uuid}.{ext} → URL pública.

    MIME permitidos: image/jpeg | image/png | image/webp. Max 10MB (bucket enforced).
    """
    return await _upload_bytes(
        image_bytes, mime_type, _IMAGES_BUCKET, _IMAGE_MIME_TO_EXT, client_id,
    )


async def upload_video_bytes(
    video_bytes: bytes, mime_type: str, client_id: Optional[str] = None,
) -> str:
    """Sube video a generated-videos/{client_id|shared}/{uuid}.{ext} → URL pública.

    MIME permitidos: video/mp4. Max 500MB (bucket enforced).
    """
    return await _upload_bytes(
        video_bytes, mime_type, _VIDEOS_BUCKET, _VIDEO_MIME_TO_EXT, client_id,
    )
