"""Pydantic models for sub-brands."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubBrand(BaseModel):
    id: str
    client_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SubBrandCreate(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class SubBrandListResponse(BaseModel):
    success: bool
    data: list[SubBrand]
    total: int


class SubBrandResponse(BaseModel):
    success: bool
    data: SubBrand
