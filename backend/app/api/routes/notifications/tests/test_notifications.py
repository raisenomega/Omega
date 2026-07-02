"""GET /notifications + PATCH /{id}/read · del usuario ACTUAL. 401 sin token · scope por user_id."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

mod = importlib.import_module("app.api.routes.notifications.router")


def _patch(monkeypatch, items, cap=None):
    async def gcu(auth):
        if not auth:
            raise HTTPException(status_code=401, detail="no auth")
        return {"id": "u1"}
    async def get_notifs(uid, limit=30):
        return items
    async def mark(nid, uid):
        if cap is not None:
            cap["marked"] = (nid, uid)
    monkeypatch.setattr(mod, "get_current_user", gcu)
    monkeypatch.setattr(mod, "get_supabase_service", lambda: SimpleNamespace(get_notifications=get_notifs, mark_notification_read=mark))


def test_list_unread_count(monkeypatch):
    _patch(monkeypatch, [{"id": "n1", "is_read": False}, {"id": "n2", "is_read": True}])
    out = asyncio.run(mod.list_notifications("Bearer x"))
    assert out.data["unread"] == 1 and len(out.data["notifications"]) == 2


def test_list_sin_token_401(monkeypatch):
    _patch(monkeypatch, [])
    with pytest.raises(HTTPException) as e:
        asyncio.run(mod.list_notifications(None))
    assert e.value.status_code == 401


def test_mark_read_scope_por_usuario(monkeypatch):
    cap: dict = {}
    _patch(monkeypatch, [], cap=cap)
    asyncio.run(mod.mark_read("n1", "Bearer x"))
    assert cap["marked"] == ("n1", "u1")  # marca con el uid del token, no del path
