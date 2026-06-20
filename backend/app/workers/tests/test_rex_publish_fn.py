"""Test del selector publish_fn de REX · DOBLE LLAVE (maestro global AND flag por-reseller).

Garantía: si CUALQUIERA de las dos llaves está OFF → shadow (publish_scheduled_post
INALCANZABLE). Solo ambas ON → live. Es lo que aísla el dogfooding por-reseller.
"""
import asyncio

import pytest

import app.workers.rex_publish_fn as fn
import app.bc_cognition.infrastructure.rex_publish_repository as repo


def _keys(monkeypatch: pytest.MonkeyPatch, master: bool, reseller: bool) -> None:
    monkeypatch.setattr(repo, "rex_live_enabled", lambda: master)
    monkeypatch.setattr(repo, "reseller_rex_live", lambda cid: reseller)


def test_master_off_is_shadow(monkeypatch: pytest.MonkeyPatch) -> None:
    _keys(monkeypatch, master=False, reseller=True)   # reseller ON pero maestro OFF → nadie publica

    async def _boom(post_id: str, client_id: str) -> None:
        raise AssertionError("publish_scheduled_post NO debe llamarse con maestro OFF")
    monkeypatch.setattr(fn, "publish_scheduled_post", _boom)

    pub = fn.select_publish_fn("c1")
    assert pub is fn._shadow_publish
    ok, reason = asyncio.run(pub("p1", "c1"))
    assert ok is False and reason == "shadow_mode"


def test_master_on_reseller_off_is_shadow(monkeypatch: pytest.MonkeyPatch) -> None:
    _keys(monkeypatch, master=True, reseller=False)   # maestro ON pero el reseller NO → shadow
    assert fn.select_publish_fn("c1") is fn._shadow_publish


def test_both_on_is_live(monkeypatch: pytest.MonkeyPatch) -> None:
    _keys(monkeypatch, master=True, reseller=True)    # las dos llaves ON → live
    called: list[str] = []

    class _Res:
        published = True
        platform_post_id = "X"
        error = None

    async def _ok(post_id: str, client_id: str) -> _Res:
        called.append(post_id)
        return _Res()
    monkeypatch.setattr(fn, "publish_scheduled_post", _ok)

    pub = fn.select_publish_fn("c1")
    assert pub is fn._live_publish
    ok, reason = asyncio.run(pub("p9", "c1"))
    assert ok is True and reason is None and called == ["p9"]
