"""
OMEGA · Reseller Home Models
R-LINES-001: < 200L · R-DDD-001: Router → Service → Repository
"""
from typing import Optional
from pydantic import BaseModel


class ResellerSocialAccount(BaseModel):
    id: str
    platform: str
    username: Optional[str]
    connected: bool
    is_active: bool


class ResellerUpcomingPost(BaseModel):
    id: str
    scheduled_date: str
    scheduled_time: Optional[str]
    text_content: Optional[str]
    status: str
    platform: Optional[str]
    has_connected_account: bool


class ResellerClientAlert(BaseModel):
    type: str       # "disconnected_account" | "post_expired" | "near_limit" | "no_activity"
    message: str
    severity: str   # "warning" | "critical"


class ResellerClientStats(BaseModel):
    posts_this_month: int
    connected_accounts: int
    total_accounts: int
    revenue_monthly: float
    plan: str


class ResellerClientData(BaseModel):
    id: str
    name: str
    email: str
    plan: str
    status: str
    health: str         # "green" | "yellow" | "red"
    social_accounts: list[ResellerSocialAccount]
    upcoming_posts: list[ResellerUpcomingPost]
    stats: ResellerClientStats
    alerts: list[ResellerClientAlert]
    last_activity_days: int


class ResellerAgentReport(BaseModel):
    agent_code: str
    agent_name: str
    client_id: str
    client_name: str
    summary: str
    created_at: str
    severity: str   # "info" | "warning" | "opportunity"


class ResellerUpsellOpportunity(BaseModel):
    client_id: str
    client_name: str
    type: str       # "near_limit" | "upgrade" | "onboarding" | "churn_risk"
    message: str
    cta: str
    potential_revenue_min: float
    potential_revenue_max: float


class ResellerKPIs(BaseModel):
    mrr_generated: float
    mrr_prev_month: float
    mrr_delta: float
    total_posts_month: int
    active_alerts: int
    healthy_clients: int
    warning_clients: int
    critical_clients: int


class ResellerProfile(BaseModel):
    id: str
    email: str
    name: str
    company: Optional[str]
    plan: str
    reseller_plan: str
    max_clients: int
    active_clients: int
    payment_status: str   # "active" | "warning" | "overdue"


class ResellerHomeData(BaseModel):
    profile: ResellerProfile
    kpis: ResellerKPIs
    clients: list[ResellerClientData]
    agent_reports: list[ResellerAgentReport]
    upsell_opportunities: list[ResellerUpsellOpportunity]


class ResellerHomeResponse(BaseModel):
    success: bool
    data: Optional[ResellerHomeData]
    error: Optional[str] = None
