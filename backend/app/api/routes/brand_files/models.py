"""
Brand Files Domain Models
Pydantic schemas for brand file management.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BrandFileProfile(BaseModel):
    """Complete brand file profile from database"""
    id: str
    client_id: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    storage_url: Optional[str] = None
    created_at: Optional[datetime] = None


class BrandFileResponse(BaseModel):
    """Standard API response for single file operations"""
    success: bool
    data: Optional[BrandFileProfile] = None
    message: Optional[str] = None
    error: Optional[str] = None


class BrandFileListResponse(BaseModel):
    """API response for file listing"""
    success: bool
    data: List[BrandFileProfile] = []
    total: int = 0
    total_size: int = 0
    message: Optional[str] = None
