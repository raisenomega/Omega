"""Sub-brands router."""
from typing import Optional
from fastapi import APIRouter, Header
from .sub_brand_models import SubBrandCreate, SubBrandListResponse, SubBrandResponse
from .sub_brand_handlers import get_sub_brands, create_sub_brand

router = APIRouter()


@router.get(
    "/clients/{client_id}/sub-brands/",
    response_model=SubBrandListResponse,
    summary="List client sub-brands",
)
async def list_sub_brands(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> SubBrandListResponse:
    return await get_sub_brands(client_id, authorization)


@router.post(
    "/clients/{client_id}/sub-brands/",
    response_model=SubBrandResponse,
    summary="Create sub-brand",
    status_code=201,
)
async def post_sub_brand(
    client_id: str,
    payload: SubBrandCreate,
    authorization: Optional[str] = Header(None),
) -> SubBrandResponse:
    return await create_sub_brand(client_id, payload, authorization)
