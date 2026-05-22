"""Storage uploader · bytes → URL pública en Supabase Storage.

Usado por _image_compat (Sprint 2 P1 · DEBT-018) y eventualmente
_video_compat (DEBT-019). Service role bypasses RLS para escritura.

Diferencia con otros repos: NO best-effort. Si falla, raise StorageUploadError
(la imagen generada sin URL persistida es output inútil · debe abortar el flow).
"""
import uuid
from typing import Final, Optional

from app.infrastructure.supabase_service import get_supabase_service


_IMAGE_MIME_TO_EXT: Final[dict[str, str]] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

_IMAGES_BUCKET: Final[str] = "generated-images"


class StorageUploadError(Exception):
    """Falla al subir bytes a Supabase Storage."""


def upload_image_bytes(
    image_bytes: bytes, mime_type: str, client_id: Optional[str] = None,
) -> str:
    """Sube imagen a generated-images/{client_id|shared}/{uuid}.{ext} → URL pública.

    Args:
      image_bytes: contenido raw de la imagen (max 10MB · enforced por bucket)
      mime_type: image/jpeg | image/png | image/webp
      client_id: opcional UUID del cliente. Si None → folder 'shared/' (legacy
                 callers sin contexto de tenant · ej. content_lab LV1 handler).

    Returns: URL https://<project>.supabase.co/storage/v1/object/public/generated-images/{path}

    Raises: StorageUploadError si MIME inválido o Supabase rechaza el upload.
    """
    ext = _IMAGE_MIME_TO_EXT.get(mime_type)
    if not ext:
        raise StorageUploadError(
            f"MIME no soportado: {mime_type!r} · "
            f"permitidos: {sorted(_IMAGE_MIME_TO_EXT)}"
        )
    path = f"{client_id or 'shared'}/{uuid.uuid4().hex}.{ext}"
    sb = get_supabase_service().client
    try:
        sb.storage.from_(_IMAGES_BUCKET).upload(
            path=path,
            file=image_bytes,
            file_options={"content-type": mime_type, "upsert": "false"},
        )
    except Exception as e:
        raise StorageUploadError(
            f"upload failed · client={client_id} bucket={_IMAGES_BUCKET} "
            f"path={path}: {e}"
        ) from e
    return sb.storage.from_(_IMAGES_BUCKET).get_public_url(path)
