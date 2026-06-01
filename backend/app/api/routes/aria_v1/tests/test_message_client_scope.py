"""Switcher V1 · ARIA message contextualizada al negocio activo (DEBT-ARIA-CHAT-CLIENT-ID).
Estilo monkeypatch + asyncio.run (igual que test_strategies_generate_handler.py). G9 exime tests.

═══════════════════════════════════════════════════════════════════════════════
PROTOCOLO DE VERIFICACIÓN MANUAL — aislamiento multi-negocio (4 tests)
═══════════════════════════════════════════════════════════════════════════════
Estos unit tests cubren la lógica; el protocolo de abajo es la verificación E2E
en producción (con `reseller@omega.com` y 2 negocios A/B). Pasó 100% al cerrar el
Switcher V1 (commits f4576fc..5bffb55). Rescatado del RECALL al eliminarlo (1 jun).
Re-correr este protocolo si se toca el flujo de ARIA chat / historial / memoria.

  Test 1 — Context y level por negocio:
    · Activar negocio A → ARIA chat → "¿quién soy?" → responde identidad de A
    · Cambiar a negocio B → "¿quién soy?" → responde identidad de B

  Test 2 — Historial aislado:
    · En negocio B, mirar chat → NO ve mensajes escritos en negocio A
    · Volver a A → ve SOLO mensajes de A

  Test 3 — Cross-contamination (el bonus crítico):
    · En A decir "mi producto estrella es X-buzón" (algo único)
    · Cambiar a B, preguntar "¿cuál es mi producto estrella?" → NO menciona X-buzón
    · Volver a A, preguntar lo mismo → recuerda X-buzón
    · NOTA: usar frases NUEVAS post-deploy (mensajes legacy pre-Commit-B quedaron
      con client_id del 1er cliente · DEBT-ARIA-LEGACY-HISTORY-CROSS-CONTAMINATION)

  Test 4 — DELETE por negocio:
    · En B borrar historial → chat de B vacío
    · Cambiar a A → chat de A INTACTO (no se borró)

Cobertura unit relacionada: este archivo (context/level por negocio) +
infrastructure/tests/test_aria_history_scope.py (historial + DELETE scoped).
═══════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.api.routes.aria_v1.handlers import message as msg
from app.api.routes.aria_v1.models import ARIAMessageRequest


def test_message_con_client_id_resuelve_target(monkeypatch):
    """client_id presente → resolve_client_or_403 + level del target pasado al use case."""
    monkeypatch.setattr(msg, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    monkeypatch.setattr(msg, "resolve_client_or_403", lambda uid, cid: {"id": cid, "aria_level": 3})
    captured = {}

    async def _use(user_id, user_message, client_id=None, level=None):
        captured.update(client_id=client_id, level=level)
        r = type("R", (), {"content": "ok", "aria_level": level})()
        return r, None
    monkeypatch.setattr(msg, "use_aria_message", _use)
    out = asyncio.run(msg.aria_message(ARIAMessageRequest(content="hola", client_id="biz-X"), "auth"))
    assert captured["client_id"] == "biz-X" and captured["level"] == 3
    assert out.aria_level == 3


def test_message_sin_client_id_es_legacy(monkeypatch):
    """client_id ausente → use case recibe None/None → cae a resolve_role LIMIT 1."""
    monkeypatch.setattr(msg, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    captured = {}

    async def _use(user_id, user_message, client_id=None, level=None):
        captured.update(client_id=client_id, level=level)
        r = type("R", (), {"content": "ok", "aria_level": 2})()
        return r, None
    monkeypatch.setattr(msg, "use_aria_message", _use)
    asyncio.run(msg.aria_message(ARIAMessageRequest(content="hola"), "auth"))
    assert captured["client_id"] is None and captured["level"] is None


def test_message_client_id_no_accesible_403(monkeypatch):
    monkeypatch.setattr(msg, "get_current_user", AsyncMock(return_value={"id": "user-1"}))

    def _deny(uid, cid):
        raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(msg, "resolve_client_or_403", _deny)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(msg.aria_message(ARIAMessageRequest(content="hola", client_id="ajeno"), "auth"))
    assert ei.value.status_code == 403


def test_message_level_per_client(monkeypatch):
    """client A (Pro=3) vs client B (Solo=1) → cada uno propaga su level real al use case."""
    monkeypatch.setattr(msg, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    levels = {"A": 3, "B": 1}
    monkeypatch.setattr(msg, "resolve_client_or_403", lambda uid, cid: {"id": cid, "aria_level": levels[cid]})
    seen = {}

    async def _use(user_id, user_message, client_id=None, level=None):
        seen[client_id] = level
        return type("R", (), {"content": "ok", "aria_level": level})(), None
    monkeypatch.setattr(msg, "use_aria_message", _use)
    asyncio.run(msg.aria_message(ARIAMessageRequest(content="x", client_id="A"), "auth"))
    asyncio.run(msg.aria_message(ARIAMessageRequest(content="x", client_id="B"), "auth"))
    assert seen == {"A": 3, "B": 1}
