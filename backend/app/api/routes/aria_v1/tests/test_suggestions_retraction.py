"""Tests · retracción de Sugerencias ARIA stale (DEBT-ARIA-SUGGESTIONS · 20 jun).

Una sugerencia unread persistía tras dejar de aplicar su condición (ej. negocio sube de
basic→enterprise pero seguía mostrando "upgrade a PRO"). El fix retracta SOLO en negativo
DETERMINADO; si la señal es indeterminada (query falla / dato ausente) NO retracta (P1).
Todo mockeado · sin red ni DB real · scope por client_id.
"""
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

import app.api.routes.aria_v1.handlers.suggestions_create as sc
from app.api.routes.aria_v1.models import ARIASuggestionsCreateRequest

_CLIENT = {"id": "biz1", "business_email": "a@b.com", "website": "w", "industry": "i", "aria_level": 4}
_RECENT = (True, datetime.now(timezone.utc))  # published_signal determinable + reciente


def _setup(monkeypatch: pytest.MonkeyPatch, *, plan, published=_RECENT, client=_CLIENT):
    inserted: list[tuple[str, str]] = []
    retracted: list[tuple[str, str]] = []
    monkeypatch.setattr(sc, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(sc, "resolve_client_or_403", lambda uid, cid: client)
    monkeypatch.setattr(sc.repo, "client_plan", lambda cid: plan)
    monkeypatch.setattr(sc.repo, "published_signal", lambda cid: published)
    monkeypatch.setattr(sc.repo, "unread_type_exists", lambda cid, st: False)
    monkeypatch.setattr(sc.writer, "insert_suggestion",
                        lambda cid, uid, msg, st: bool(inserted.append((cid, st))) or True)
    monkeypatch.setattr(sc.writer, "retract_unread",
                        lambda cid, st: bool(retracted.append((cid, st))) or 1)
    monkeypatch.setattr(sc.writer, "list_suggestions", lambda cid, unread_only: [])
    return inserted, retracted


def _run(client_id: str = "biz1"):
    return asyncio.run(sc.aria_suggestions_create(ARIASuggestionsCreateRequest(client_id=client_id), "Bearer x"))


def test_plan_basic_to_enterprise_retracts_stale_upgrade(monkeypatch: pytest.MonkeyPatch) -> None:
    # EL BUG: el negocio ya es enterprise (plan != basic) → 'upgrade_plan' caducó → se auto-cierra.
    inserted, retracted = _setup(monkeypatch, plan="enterprise")
    out = _run()
    assert ("biz1", "upgrade_plan") in retracted           # stale auto-cerrada
    assert ("biz1", "upgrade_plan") not in inserted         # no aplica → no emite
    assert all(cid == "biz1" for cid, _ in retracted)       # scope: solo ESE negocio
    assert out.generated == 0


def test_indeterminate_plan_does_not_retract(monkeypatch: pytest.MonkeyPatch) -> None:
    # client_plan None (query falló / sin fila) → indeterminado → NI emite NI retracta (no agresivo).
    inserted, retracted = _setup(monkeypatch, plan=None)
    _run()
    assert ("biz1", "upgrade_plan") not in retracted        # conserva ante señal indeterminada
    assert ("biz1", "upgrade_plan") not in inserted


def test_plan_basic_still_inserts_upgrade(monkeypatch: pytest.MonkeyPatch) -> None:
    # Camino positivo intacto: basic → 'upgrade_plan' aplica → se emite, NO se retracta.
    inserted, retracted = _setup(monkeypatch, plan="basic")
    _run()
    assert ("biz1", "upgrade_plan") in inserted
    assert ("biz1", "upgrade_plan") not in retracted
