"""GUARDIAN · repository (infra · A9 infra→domain). Reads/writes tablas 00022.

Lee user_security_log + ip_watchlist · escribe user_security_log + security_incidents.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from app.bc_cognition.domain.guardian_threats import SecurityEvent
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


def fetch_recent_events(supabase: SupabaseService, user_id: str, hours: int = 24) -> Tuple[SecurityEvent, ...]:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    r = supabase.client.table("user_security_log").select(
        "event_type, ip_address, user_agent, created_at"
    ).eq("user_id", user_id).gte("created_at", cutoff).order("created_at", desc=True).limit(100).execute()
    return tuple(
        SecurityEvent(
            row["event_type"], row.get("ip_address") or "", row.get("user_agent") or "",
            datetime.fromisoformat(row["created_at"]),
        )
        for row in (r.data or [])
    )


def lookup_ip(supabase: SupabaseService, ip: str) -> Optional[str]:
    r = supabase.client.table("ip_watchlist").select("list_type").eq("ip_address", ip).limit(1).execute()
    return r.data[0]["list_type"] if r.data else None


def insert_security_log(supabase: SupabaseService, user_id: str, ip: str, user_agent: str,
                        event_type: str, risk_score: int, signals: List[str]) -> None:
    supabase.client.table("user_security_log").insert({
        "user_id": user_id, "ip_address": ip, "user_agent": user_agent,
        "event_type": event_type, "risk_score": risk_score, "metadata": {"signals": signals},
    }).execute()


def insert_incident(supabase: SupabaseService, user_id: str, incident_type: str,
                    severity: str, signals: List[str]) -> None:
    supabase.client.table("security_incidents").insert({
        "user_id": user_id, "incident_type": incident_type, "severity": severity,
        "summary": f"GUARDIAN: {incident_type}", "evidence": {"signals": signals},
    }).execute()


def fetch_session_summary(supabase: SupabaseService, user_id: str, limit: int = 10) -> dict:
    """Resumen para SecurityKPICard (4B-3): último login, eventos recientes, incidentes abiertos."""
    logs = supabase.client.table("user_security_log").select(
        "event_type, ip_address, created_at, risk_score, metadata"
    ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    rows = logs.data or []
    inc = supabase.client.table("security_incidents").select(
        "id", count="exact").eq("user_id", user_id).eq("status", "open").execute()
    open_count = inc.count or 0
    last = next(({"at": r["created_at"], "ip": r.get("ip_address") or ""}
                 for r in rows if r["event_type"] == "login_success"), None)
    signals = sorted({s for r in rows for s in (r.get("metadata") or {}).get("signals", [])})
    return {
        "status": "revisar" if open_count else "protegida",
        "last_login": last,
        "recent_events": [{"event_type": r["event_type"], "ip": r.get("ip_address") or "",
                           "at": r["created_at"], "risk_score": r.get("risk_score") or 0} for r in rows],
        "open_incidents": open_count,
        "active_signals": signals,
    }
