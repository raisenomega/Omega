"""Test del worker REX · filtra clientes (add-on+toggle) y delega al UC con la publish_fn del wrapper."""
import asyncio
from typing import Optional

import pytest

import app.workers.rex_publisher_worker as w
import app.bc_cognition.infrastructure.rex_publish_repository as repo


def test_get_active_clients_filters_by_addon_and_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(repo, "fetch_active_rex_client_ids", lambda: ["a", "b"])
    out = asyncio.run(w.rex_publisher_worker._get_active_clients())
    assert out == ["a", "b"]


def test_execute_delegates_to_uc_with_selected_fn(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    async def _shadow(post_id: str, client_id: str) -> tuple[bool, Optional[str]]:
        return (False, "shadow_mode")

    async def _run(cid: str, fn: object) -> dict[str, str]:
        seen["cid"] = cid
        seen["fn"] = fn
        return {"client_id": cid}

    seen_fn_arg: dict[str, str] = {}

    def _select(client_id: str) -> object:
        seen_fn_arg["cid"] = client_id   # el wrapper recibe el client_id (doble llave por-cliente)
        return _shadow
    monkeypatch.setattr(w, "select_publish_fn", _select)
    monkeypatch.setattr(w, "run_rex_for_client", _run)
    out = asyncio.run(w.rex_publisher_worker.execute("c9"))
    assert out == {"client_id": "c9"}
    assert seen["cid"] == "c9" and seen["fn"] is _shadow   # usó la fn que dio el wrapper
    assert seen_fn_arg["cid"] == "c9"                       # select_publish_fn(client_id), no global
