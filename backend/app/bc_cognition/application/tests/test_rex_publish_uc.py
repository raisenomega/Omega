"""Tests de orquestación REX (F2) · UC flag-agnóstico: recibe publish_fn inyectada.

hold registra+sigue (publish_fn NUNCA se llama) · shadow-fn → registra sin publicar (published_at
NULL) · live-fn éxito → publica · live-fn fallo → registro honesto · fail-safe gating.
"""
import asyncio
from typing import Any, Optional

import pytest

import app.bc_cognition.application.rex_publish_uc as uc
import app.bc_cognition.infrastructure.rex_publish_repository as repo
import app.bc_cognition.infrastructure.aria_memory_repository as mem
from app.bc_cognition.domain.brand_voice_scorer_prompt import SCORE_BRAND_BAR


def _gating(**over: object) -> dict[str, Any]:
    base: dict[str, Any] = {"rex_addon_active": True, "autonomous_mode_on": True,
                            "crisis_active": False, "user_id": "u1", "reseller_id": "r1"}
    base.update(over)
    return base


def _post(pid: str = "p1", sa: str = "sa1") -> dict[str, Any]:
    return {"id": pid, "client_id": "cli1", "content_id": "c1", "social_account_id": sa,
            "scheduled_for": "2026-06-20T10:00:00+00:00", "media_url": "http://x/m.jpg"}


def _setup(monkeypatch: pytest.MonkeyPatch, *, gating: Optional[dict[str, Any]],
           due: list[dict[str, Any]], published_by_platform: Optional[dict[str, int]] = None,
           account_by_sa: Optional[dict[str, str]] = None) -> list[dict[str, Any]]:
    logs: list[dict[str, Any]] = []
    content = {"confidence": 7, "brand_voice_score": SCORE_BRAND_BAR}
    plats = account_by_sa or {}            # social_account_id → platform (default facebook)
    counts = published_by_platform or {}   # conteo previo POR RED (default vacío = 0)
    monkeypatch.setattr(repo, "fetch_client_gating", lambda cid: gating)
    monkeypatch.setattr(repo, "fetch_due_posts", lambda cid, lim: due)
    monkeypatch.setattr(repo, "fetch_content_signals", lambda cid: content)
    monkeypatch.setattr(repo, "fetch_account_binding", lambda sid: {
        "platform": plats.get(sid, "facebook"), "zernio_account_id": "z1", "status": "active"})
    monkeypatch.setattr(repo, "count_published_today_by_platform", lambda cid: dict(counts))
    monkeypatch.setattr(repo, "insert_rex_publish_log", lambda row: logs.append(row))
    monkeypatch.setattr(mem, "insert_agent_memory", lambda *a, **k: None)
    monkeypatch.setattr(uc, "get_supabase_service", lambda: object())
    return logs


def _live_fn(pubs: list[str], ok: bool) -> uc.PublishFn:
    async def f(post_id: str, client_id: str) -> tuple[bool, Optional[str]]:
        pubs.append(post_id)
        return (ok, None if ok else "publish_failed:boom")
    return f


async def _shadow_fn(post_id: str, client_id: str) -> tuple[bool, Optional[str]]:
    """Simula el wrapper con REX_LIVE OFF: NO publica, devuelve shadow_mode."""
    return (False, "shadow_mode")


def test_skip_gating_off(monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(monkeypatch, gating=_gating(autonomous_mode_on=False), due=[_post()])
    assert asyncio.run(uc.run_rex_for_client("cli1", _shadow_fn))["skipped"] == "gating_off"


def test_skip_gating_unreadable(monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(monkeypatch, gating=None, due=[_post()])
    assert asyncio.run(uc.run_rex_for_client("cli1", _shadow_fn))["skipped"] == "gating_unreadable"


def test_hold_records_and_never_calls_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    # crisis_active=True → ambos holdean · publish_fn NUNCA se invoca (aun con live-fn)
    logs = _setup(monkeypatch, gating=_gating(crisis_active=True), due=[_post("p1"), _post("p2")])
    pubs: list[str] = []
    out = asyncio.run(uc.run_rex_for_client("cli1", _live_fn(pubs, True)))
    assert out["holds"] == 2 and out["published"] == 0 and pubs == []
    assert all(r["gate_result"] == "hold" and r["hold_reason"] == "crisis_active" for r in logs)


def test_shadow_fn_records_publish_without_publishing(monkeypatch: pytest.MonkeyPatch) -> None:
    logs = _setup(monkeypatch, gating=_gating(), due=[_post()])
    out = asyncio.run(uc.run_rex_for_client("cli1", _shadow_fn))
    assert out["published"] == 0                                   # no contó como publicado
    assert len(logs) == 1 and logs[0]["gate_result"] == "publish"  # el gate sí dijo publish
    assert logs[0]["hold_reason"] == "shadow_mode" and logs[0]["published_at"] is None


def test_live_fn_success_publishes(monkeypatch: pytest.MonkeyPatch) -> None:
    logs = _setup(monkeypatch, gating=_gating(), due=[_post("p9")])
    pubs: list[str] = []
    out = asyncio.run(uc.run_rex_for_client("cli1", _live_fn(pubs, True)))
    assert out["published"] == 1 and pubs == ["p9"]
    assert logs[0]["gate_result"] == "publish" and logs[0]["published_at"] is not None


def test_live_fn_failure_recorded_honestly(monkeypatch: pytest.MonkeyPatch) -> None:
    logs = _setup(monkeypatch, gating=_gating(), due=[_post("p9")])
    pubs: list[str] = []
    out = asyncio.run(uc.run_rex_for_client("cli1", _live_fn(pubs, False)))
    assert out["published"] == 0 and pubs == ["p9"]
    assert logs[0]["published_at"] is None and "publish_failed" in logs[0]["hold_reason"]
