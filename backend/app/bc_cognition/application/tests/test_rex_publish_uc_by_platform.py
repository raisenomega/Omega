"""Tests REX · conteo de publicación POR RED (DEBT-098 · cada red su cupo).

Arregla el bug del 20 jun: 3 posts a la misma hora en 3 redes distintas → solo 1 publicaba
por el conteo COMBINADO. Reusa el harness de test_rex_publish_uc (mismo patrón que
test_aria_tools_content_id importa de test_aria_tools).
"""
import asyncio

import pytest

import app.bc_cognition.application.rex_publish_uc as uc
from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA
from app.bc_cognition.application.tests.test_rex_publish_uc import _gating, _live_fn, _post, _setup


def test_tres_redes_misma_hora_publican_las_3(monkeypatch: pytest.MonkeyPatch) -> None:
    """EL BUG: 3 posts a la misma hora en 3 redes distintas. Con conteo COMBINADO el 3er+
    holdeaba ('daily_limit_reached'); con conteo POR RED (cada una en 0) los 3 publican."""
    due = [_post("p1", "saIG"), _post("p2", "saFB"), _post("p3", "saTT")]
    account_by_sa = {"saIG": "instagram", "saFB": "facebook", "saTT": "tiktok"}
    logs = _setup(monkeypatch, gating=_gating(), due=due,
                  published_by_platform={}, account_by_sa=account_by_sa)
    pubs: list[str] = []
    out = asyncio.run(uc.run_rex_for_client("cli1", _live_fn(pubs, True)))
    assert out["published"] == 3 and out["holds"] == 0
    assert sorted(pubs) == ["p1", "p2", "p3"]
    assert all(r["gate_result"] == "publish" for r in logs)
    assert not any(r.get("hold_reason") == "daily_limit_reached" for r in logs)


def test_cap_por_red_holdea_overflow(monkeypatch: pytest.MonkeyPatch) -> None:
    """El cap sigue vivo PERO por red: IG ya en el tope holdea; FB (en 0) publica."""
    cap = LIMITS_OMEGA["MAX_POSTS_AUTO_PER_DIA_RED"]
    due = [_post("pIG", "saIG"), _post("pFB", "saFB")]
    account_by_sa = {"saIG": "instagram", "saFB": "facebook"}
    logs = _setup(monkeypatch, gating=_gating(), due=due,
                  published_by_platform={"instagram": cap}, account_by_sa=account_by_sa)
    pubs: list[str] = []
    out = asyncio.run(uc.run_rex_for_client("cli1", _live_fn(pubs, True)))
    assert out["published"] == 1 and pubs == ["pFB"]
    ig_log = next(r for r in logs if r["platform"] == "instagram")
    fb_log = next(r for r in logs if r["platform"] == "facebook")
    assert ig_log["gate_result"] == "hold" and ig_log["hold_reason"] == "daily_limit_reached"
    assert fb_log["gate_result"] == "publish" and fb_log["published_at"] is not None
