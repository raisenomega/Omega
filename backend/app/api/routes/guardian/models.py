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


class SecurityEventOut(BaseModel):
    event_type: str
    ip: str
    at: str
    risk_score: int


class SessionReportResponse(BaseModel):
    status: str
    last_login: Optional[LastLogin]
    recent_events: List[SecurityEventOut]
    open_incidents: int
    active_signals: List[str]
