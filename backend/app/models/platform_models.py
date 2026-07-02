"""Models for platform public landing endpoints (marca OMEGA · sin auth)."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class CreatePlatformLeadRequest(BaseModel):
    """Lead de la landing pública de plataforma.

    reseller_id se fuerza NULL en el handler (no está en el body · lead de plataforma).
    audience se restringe a pyme|reseller (2ª barrera = CHECK de la tabla leads · 00084).
    website es honeypot: campo oculto que los bots llenan y los humanos no.
    """
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    message: Optional[str] = Field(None, max_length=2000)
    audience: Literal["pyme", "reseller"] = "pyme"
    website: str = Field(default="", max_length=255)
    # Trazabilidad de embudos (D7 · opcional): el handler valida ^[a-z0-9_-]{1,50}$ y cae a
    # 'omega_landing' si falta o no valida (NO 422 · embudos futuros sin deploy · NO whitelist fija).
    source: Optional[str] = Field(None, max_length=50)
