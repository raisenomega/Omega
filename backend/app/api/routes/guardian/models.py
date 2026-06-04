"""GUARDIAN · request/response models (4B-3)."""
from typing import List, Optional
from pydantic import BaseModel


class LoginEventRequest(BaseModel):
    success: bool


class LoginEventResponse(BaseModel):
    action: str
    risk_score: int
    signals: List[str]


class LastLogin(BaseModel):
    at: str
    ip: str
    country: Optional[str] = None


class SecurityEventOut(BaseModel):
    event_type: str
    ip: str
    country: Optional[str] = None
    at: str
    risk_score: int


class SessionReportResponse(BaseModel):
    status: str
    last_login: Optional[LastLogin]
    recent_events: List[SecurityEventOut]
    open_incidents: int
    active_signals: List[str]


# ── Acciones owner end-to-end (4B-1 · gated require_superadmin) ──
class BlockIpRequest(BaseModel):
    ip_address: str
    reason: Optional[str] = None
    scope_client_id: Optional[str] = None
    expires_at: Optional[str] = None
    incident_id: Optional[str] = None


class ForceLogoutRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None
    incident_id: Optional[str] = None


class ResolveIncidentRequest(BaseModel):
    incident_id: str
    resolution_notes: Optional[str] = None
    false_positive: bool = False  # True → status='false_positive' · False → 'resolved'


class PasswordResetRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None
    incident_id: Optional[str] = None
