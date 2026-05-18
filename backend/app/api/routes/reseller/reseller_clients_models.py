"""
OMEGA · Reseller Clients Models
Pydantic DTOs for GET /api/v1/reseller/{reseller_id}/clients/
R-LINES-001: < 200L
"""
from typing import Optional, List
from pydantic import BaseModel


class ResellerClientItem(BaseModel):
    """Single client in reseller's portfolio"""
    id: str
    name: str
    email: str
    plan: str
    status: str
    health: str  # "green" | "yellow" | "red"
    posts_this_month: int
    connected_accounts: int
    total_accounts: int
    alerts_count: int
    last_post_date: Optional[str] = None
    revenue_monthly: float


class ResellerClientListData(BaseModel):
    """List of clients with summary stats"""
    clients: List[ResellerClientItem]
    total_clients: int
    reseller_id: str
    reseller_name: str
    reseller_plan: str
    max_clients: int


class ResellerClientListResponse(BaseModel):
    """Response wrapper for clients list"""
    success: bool
    data: Optional[ResellerClientListData] = None
    error: Optional[str] = None
