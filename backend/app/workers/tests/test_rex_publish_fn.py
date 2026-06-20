"""Test del selector publish_fn de REX · la garantía de que OFF = REX inerte.

OFF → select_publish_fn devuelve shadow · shadow NO llama publish_scheduled_post.
ON  → devuelve live · live SÍ llama publish_scheduled_post.
"""
import asyncio

import pytest

import app.workers.rex_publish_fn as fn
import app.bc_cognition.infrastructure.rex_publish_repository as repo


def test_off_selects_shadow_and_does_not_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repo, "rex_live_enabled", lambda: False)

    async def _boom(post_id: str, client_id: str) -> None:
        raise AssertionError("publish_scheduled_post NO debe llamarse con REX_LIVE OFF")
    monkeypatch.setattr(fn, "publish_scheduled_post", _boom)

    pub = fn.select_publish_fn()
    assert pub is fn._shadow_publish
    ok, reason = asyncio.run(pub("p1", "c1"))
    assert ok is False and reason == "shadow_mode"   # registró intención · NUNCA publicó


def test_on_selects_live_and_publishes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repo, "rex_live_enabled", lambda: True)
    called: list[str] = []

    class _Res:
        published = True
        platform_post_id = "X"
        error = None

    async def _ok(post_id: str, client_id: str) -> _Res:
        called.append(post_id)
        return _Res()
    monkeypatch.setattr(fn, "publish_scheduled_post", _ok)

    pub = fn.select_publish_fn()
    assert pub is fn._live_publish
    ok, reason = asyncio.run(pub("p9", "c1"))
    assert ok is True and reason is None and called == ["p9"]   # SÍ publicó de verdad
