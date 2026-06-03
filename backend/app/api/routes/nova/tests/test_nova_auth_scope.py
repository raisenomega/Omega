"""IDOR fix · NOVA owner-only (DEBT-IDOR-NOVA · G9 exime tests).
NOVA = módulo owner (consola CEO · va al lado de Security Dev super_owner-only).
Los 11 endpoints exigen require_superadmin. Molde: analytics/tests/test_analytics_auth_scope.py.

Llamada DIRECTA a la función (no HTTP): require_superadmin es la 1ª línea del body, así que
corre ANTES de tocar el request → 401 sin auth en los 11 (request dummy nunca se usa).
NOTA: vía HTTP los POST con body inválido dan 422 (validación FastAPI precede al auth in-body);
por eso sentinel_pulse mantiene 422 para /nova/chat/ (no se tocó · sería falsa regresión)."""
import asyncio
import importlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

ar = importlib.import_module("app.api.routes.nova.router")


# (nombre, coroutine-factory) · authorization=None · request/supabase dummy (require_superadmin corre antes)
ENDPOINTS_UNAUTH = [
    ("get_data", lambda: ar.get_data(type=None, authorization=None)),
    ("save_data", lambda: ar.save_data(request=None, authorization=None)),
    ("get_agent_memory", lambda: ar.get_agent_memory(agent_code=None, authorization=None)),
    ("save_agent_memory", lambda: ar.save_agent_memory(request=None, authorization=None)),
    ("nova_chat", lambda: ar.nova_chat(request=None, authorization=None)),
    ("get_briefing", lambda: ar.get_briefing(authorization=None)),
    ("save_nova_memory", lambda: ar.save_nova_memory(request=None, authorization=None)),
    ("execute_action", lambda: ar.execute_action(request=None, authorization=None)),
    ("get_nova_context", lambda: ar.get_nova_context(client_id="X", supabase=None, authorization=None)),
    ("update_nova_context", lambda: ar.update_nova_context(client_id="X", request=None, supabase=None, authorization=None)),
    ("patch_nova_learning", lambda: ar.patch_nova_learning(client_id="X", request=None, supabase=None, authorization=None)),
]


@pytest.mark.parametrize("name,call", ENDPOINTS_UNAUTH, ids=[n for n, _ in ENDPOINTS_UNAUTH])
def test_endpoint_sin_auth_401(name, call):
    """Los 11 sin Authorization → 401 (require_superadmin → get_current_user real lanza antes de la DB)."""
    with pytest.raises(HTTPException) as e:
        asyncio.run(call())
    assert e.value.status_code == 401


def test_role_no_owner_403(monkeypatch):
    """Con token pero role != owner → require_superadmin lanza 403."""
    monkeypatch.setattr(ar, "require_superadmin",
                        AsyncMock(side_effect=HTTPException(status_code=403, detail="superadmin_only")))
    with pytest.raises(HTTPException) as e:
        asyncio.run(ar.get_data(type=None, authorization="auth"))
    assert e.value.status_code == 403


def test_role_owner_200(monkeypatch):
    """role = owner → require_superadmin OK → el handler corre (happy path)."""
    monkeypatch.setattr(ar, "require_superadmin", AsyncMock(return_value={"id": "owner", "role": "owner"}))
    monkeypatch.setattr(ar, "handle_get_data", AsyncMock(return_value=[]))
    out = asyncio.run(ar.get_data(type=None, authorization="auth"))
    assert out == []
