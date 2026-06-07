"""T1 · PATCH /content/{id}/media setea media_urls SIN tocar generated_text (P1) + ownership.
Mock de supabase/repo · cero DB real. G9 exime tests."""
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

from app.api.routes.content_v3 import _content_repository as repo
from app.api.routes.content_v3.handlers import set_media as h


def test_update_media_urls_payload_solo_media_urls():
    """P1: el UPDATE escribe SOLO media_urls · generated_text NUNCA en el payload."""
    cap = {}
    chain = SimpleNamespace()
    chain.update = lambda payload: (cap.update(payload=payload) or chain)
    chain.eq = lambda *a, **k: chain
    chain.execute = lambda: None
    with patch.object(repo, "_sb", return_value=SimpleNamespace(table=lambda n: chain)):
        repo.update_media_urls("c1", ["https://media/x.jpg"])
    assert cap["payload"] == {"media_urls": ["https://media/x.jpg"]}
    assert "generated_text" not in cap["payload"]


def test_set_media_handler_routes_to_update_media_urls():
    """El handler valida ownership y enruta a repo.update_media_urls(content_id, media_urls)."""
    captured = {}

    async def _safe_insert(label, fn, *a):
        captured["fn"] = fn; captured["args"] = a

    with patch.object(h, "get_current_user", AsyncMock(return_value={"id": "u1"})), \
         patch.object(h.reader, "get_content_item", return_value={"client_id": "client-A"}), \
         patch.object(h.reader, "get_accessible_client_ids", return_value=["client-A"]), \
         patch.object(h.repo, "safe_insert", _safe_insert):
        out = asyncio.run(h.set_media("c1", h.SetMediaRequest(media_urls=["u"]), "Bearer x"))
    assert out == {"id": "c1", "media_urls": ["u"]}
    assert captured["fn"] is h.repo.update_media_urls and captured["args"] == ("c1", ["u"])


def test_set_media_denies_foreign_client():
    """Ownership: content_id de otro dueño → 403."""
    from fastapi import HTTPException
    with patch.object(h, "get_current_user", AsyncMock(return_value={"id": "u1"})), \
         patch.object(h.reader, "get_content_item", return_value={"client_id": "OTRO"}), \
         patch.object(h.reader, "get_accessible_client_ids", return_value=["client-A"]):
        try:
            asyncio.run(h.set_media("c1", h.SetMediaRequest(media_urls=["u"]), "Bearer x"))
            assert False, "esperaba 403"
        except HTTPException as e:
            assert e.status_code == 403
