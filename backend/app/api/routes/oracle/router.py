"""
ORACLE Router
Intelligence Brief endpoints
"""
from fastapi import APIRouter
from app.api.routes.oracle.handlers import handle_get_brief, handle_generate_brief

router = APIRouter()


@router.get("/brief/")
async def get_brief():
    """Get latest ORACLE Intelligence Brief"""
    return await handle_get_brief()


@router.post("/brief/generate/")
async def generate_brief():
    """Generate new ORACLE Intelligence Brief"""
    return await handle_generate_brief()
