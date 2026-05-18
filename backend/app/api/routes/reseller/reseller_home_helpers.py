"""
OMEGA · Reseller Home Helpers
Funciones de cálculo de salud, alertas y oportunidades de upsell
R-LINES-001: < 200L
"""
from datetime import datetime, timezone, timedelta
from typing import Any

from .reseller_home_models import (
    ResellerClientAlert,
    ResellerUpsellOpportunity,
)

PLAN_LIMITS: dict[str, dict[str, Any]] = {
    "basic":      {"posts": 50,  "msgs": 250, "price": 2500.0},
    "pro":        {"posts": 150, "msgs": 600, "price": 5000.0},
    "enterprise": {"posts": None, "msgs": None, "price": 10000.0},
}

RESELLER_PLAN_CAPACITY: dict[str, int] = {
    "agency_starter": 5,
    "agency_growth":  10,
    "agency_scale":   25,
}


def get_client_revenue(plan: str) -> float:
    return PLAN_LIMITS.get(plan, {}).get("price", 2500.0)


def compute_client_health(
    social_accounts: list[dict],
    posts_count: int,
    plan: str,
    last_post_date: str | None,
) -> str:
    connected = [a for a in social_accounts if a.get("connected")]
    total = len(social_accounts)
    limit = PLAN_LIMITS.get(plan, {}).get("posts")

    # Red: no accounts at all, or payment issue, or no activity 7+ days
    if total > 0 and len(connected) == 0:
        return "red"
    if last_post_date:
        try:
            last = datetime.fromisoformat(last_post_date.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - last).days
            if days_ago >= 14:
                return "red"
        except (ValueError, AttributeError):
            pass

    # Yellow: some not connected, or near limit
    if total > 0 and len(connected) < total:
        return "yellow"
    if limit and posts_count >= int(limit * 0.8):
        return "yellow"

    return "green"


def build_client_alerts(
    client: dict,
    social_accounts: list[dict],
    posts_count: int,
    plan: str,
    last_post_date: str | None,
) -> list[ResellerClientAlert]:
    alerts: list[ResellerClientAlert] = []

    disconnected = [a for a in social_accounts if not a.get("connected")]
    for acc in disconnected:
        alerts.append(ResellerClientAlert(
            type="disconnected_account",
            message=f"{acc.get('platform','Red').capitalize()} no conectada",
            severity="critical",
        ))

    limit = PLAN_LIMITS.get(plan, {}).get("posts")
    if limit and posts_count >= int(limit * 0.8):
        pct = int((posts_count / limit) * 100)
        alerts.append(ResellerClientAlert(
            type="near_limit",
            message=f"Usando {pct}% de posts del plan",
            severity="warning",
        ))

    if last_post_date:
        try:
            last = datetime.fromisoformat(last_post_date.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - last).days
            if days_ago >= 7:
                alerts.append(ResellerClientAlert(
                    type="no_activity",
                    message=f"Sin actividad hace {days_ago} días",
                    severity="warning" if days_ago < 14 else "critical",
                ))
        except (ValueError, AttributeError):
            pass

    return alerts


def build_upsell_opportunities(
    clients: list[dict],
) -> list[ResellerUpsellOpportunity]:
    opportunities: list[ResellerUpsellOpportunity] = []

    for c in clients:
        plan = c.get("plan", "basic")
        posts = c.get("posts_month", 0)
        limit = PLAN_LIMITS.get(plan, {}).get("posts")
        name = c.get("name", "Cliente")
        cid = c.get("id", "")

        if limit and posts >= int(limit * 0.8) and plan != "enterprise":
            next_plan = "pro" if plan == "basic" else "enterprise"
            next_price = PLAN_LIMITS.get(next_plan, {}).get("price", 5000.0)
            current_price = PLAN_LIMITS.get(plan, {}).get("price", 2500.0)
            delta = next_price - current_price
            opportunities.append(ResellerUpsellOpportunity(
                client_id=cid,
                client_name=name,
                type="near_limit",
                message=f"{name} está usando {posts}/{limit} posts. Upgrade a {next_plan.capitalize()}.",
                cta=f"Proponer upgrade a {next_plan.capitalize()}",
                potential_revenue_min=delta,
                potential_revenue_max=delta * 1.5,
            ))

        if c.get("connected_accounts", 0) == 0 and c.get("days_since_created", 0) >= 7:
            opportunities.append(ResellerUpsellOpportunity(
                client_id=cid,
                client_name=name,
                type="onboarding",
                message=f"{name} lleva 7+ días sin conectar redes.",
                cta="Iniciar onboarding",
                potential_revenue_min=0,
                potential_revenue_max=500,
            ))

    return opportunities
