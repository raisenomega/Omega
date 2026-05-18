"""
Brand Files Router
GET    /brand-files/?client_id={id}  - List files
POST   /brand-files/upload/          - Upload file
DELETE /brand-files/{file_id}/       - Delete file
"""
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query
from typing import Optional
import logging

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service
from .models import BrandFileProfile, BrandFileResponse, BrandFileListResponse
from ._brand_files_upload import handle_upload_brand_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/brand-files", tags=["brand-files"])


@router.get("/", response_model=BrandFileListResponse)
async def list_brand_files(
    client_id: str = Query(...),
    authorization: Optional[str] = Header(None),
) -> BrandFileListResponse:
    """List all brand files for a client."""
    try:
        await get_current_user(authorization)
        supabase = get_supabase_service()

        result = supabase.client.table("brand_files")\
            .select("*")\
            .eq("client_id", client_id)\
            .order("created_at", desc=True)\
            .execute()

        files = result.data or []
        total_size = sum(f.get("file_size", 0) for f in files)

        return BrandFileListResponse(
            success=True,
            data=[BrandFileProfile(**f) for f in files],
            total=len(files),
            total_size=total_size,
            message=f"Found {len(files)} file(s)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing brand files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while listing files")


@router.post("/upload/", response_model=BrandFileResponse)
async def upload_brand_file(
    client_id: str = Query(...),
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
) -> BrandFileResponse:
    """Upload brand file to Supabase Storage. Validates plan limits and file types."""
    try:
        await get_current_user(authorization)
        return await handle_upload_brand_file(client_id, file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading brand file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while uploading file")


@router.delete("/{file_id}/", response_model=BrandFileResponse)
async def delete_brand_file(
    file_id: str,
    authorization: Optional[str] = Header(None),
) -> BrandFileResponse:
    """Delete brand file from Storage and database."""
    try:
        await get_current_user(authorization)
        supabase = get_supabase_service()

        file_result = supabase.client.table("brand_files")\
            .select("*")\
            .eq("id", file_id)\
            .single()\
            .execute()

        if not file_result.data:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        file_record = file_result.data

        supabase.client.storage.from_("brand-guides").remove([file_record["file_path"]])
        supabase.client.table("brand_files").delete().eq("id", file_id).execute()

        logger.info(f"Brand file deleted: {file_record['file_name']} (ID: {file_id})")

        return BrandFileResponse(
            success=True,
            message=f"Archivo {file_record['file_name']} eliminado",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brand file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while deleting file")
