"""
Auth Avatar Upload Routes
Endpoint for client avatar upload to Supabase Storage
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from typing import Optional
from app.models.shared_models import APIResponse
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload-avatar", response_model=APIResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
) -> APIResponse:
    """
    Upload client avatar image (max 5MB)

    Args:
        file: Image file (image/jpeg, image/png, image/webp)
        authorization: Authorization header ("Bearer <token>")

    Returns:
        APIResponse with:
            - success: True
            - data: Object with avatar_url (public URL)
            - message: Success message

    Raises:
        HTTPException 401: Missing or invalid authorization header
        HTTPException 400: Invalid file type or size
        HTTPException 404: Client not found
        HTTPException 500: Server error

    Uploads to Supabase Storage bucket 'reseller-media' at:
        avatars/{client_id}/avatar.{extension}

    Updates clients.avatar_url with public URL
    """
    try:
        # Extract and verify client_id from token
        client_id = await get_current_user_id(authorization)

        service = get_supabase_service()

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )

        # Validate file size (5MB max)
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > 5:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size_mb:.2f}MB). Max 5MB allowed."
            )

        # Generate file path (defensive handling for None filename)
        filename = file.filename or "upload"
        file_extension = filename.split(".")[-1] if "." in filename else "jpg"
        file_path = f"avatars/{client_id}/avatar.{file_extension}"

        # Upload to Supabase Storage
        public_url = await service.upload_media(
            bucket="reseller-media",
            file_path=file_path,
            file_data=file_data,
            content_type=file.content_type
        )

        # Update client avatar_url
        update_response = service.client.table("clients")\
            .update({"avatar_url": public_url})\
            .eq("id", client_id)\
            .execute()

        if not update_response.data or len(update_response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        logger.info(f"Avatar uploaded for client: {client_id}")

        return APIResponse(
            success=True,
            data={"avatar_url": public_url},
            message="Avatar uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))
