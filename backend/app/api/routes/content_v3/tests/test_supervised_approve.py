"""P2 · tests del puente aprobar→calendario (maybe_schedule_on_approve).
Mock de cal_repo (insert) + _first_active_account_id. Cero DB real. G9 exime tests.
Decisiones: A1 (cuenta NULL si no hay) · B2 (sin fecha → no agenda) · supervisado-only."""
from unittest.mock import MagicMock
from app.api.routes.content_v3 import _supervised_approve as sa


def _item(metadata, cid="draft-1", client="client-A"):
    return {"id": cid, "client_id": client, "metadata": metadata, "generated_text": "post"}


def test_supervised_with_date_inserts_scheduled(monkeypatch):
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", lambda c, p: "acc-1")
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00", "platform": "instagram"}))
    assert out is not None and out["scheduled_for"] == "2026-06-01T15:00" and out["falta_cuenta"] is False
    row = rows["r"][0]
    assert row["client_id"] == "client-A" and row["content_id"] == "draft-1"
    assert row["social_account_id"] == "acc-1" and row["scheduled_for"] == "2026-06-01T15:00" and row["status"] == "pending"


def test_supervised_no_account_inserts_null(monkeypatch):  # A1
    captured = {}
    monkeypatch.setattr(sa, "_first_active_account_id", lambda c, p: None)
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: captured.update(r=r) or r)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-02T09:00", "platform": "tiktok"}))
    assert out["falta_cuenta"] is True
    assert captured["r"][0]["social_account_id"] is None  # nullable · agenda igual


def test_supervised_without_date_does_not_schedule(monkeypatch):  # B2
    called = MagicMock()
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "platform": "instagram"}))  # sin fecha_sugerida
    assert out is None
    called.assert_not_called()  # queda approved · cliente agenda manual


def test_non_supervised_draft_ignored(monkeypatch):
    called = MagicMock()
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"fecha_sugerida": "2026-06-01T15:00"}))  # sin supervisado=true
    assert out is None
    called.assert_not_called()


def test_media_urls_propagates_to_scheduled_media_url(monkeypatch):  # foto adjunta → publisher
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", lambda c, p: "acc-1")
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    item = {**_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00", "platform": "instagram"}),
            "media_urls": ["https://media/x.jpg"]}
    sa.maybe_schedule_on_approve(item)
    assert rows["r"][0]["media_url"] == "https://media/x.jpg"  # el publisher ya lee media_url


def test_no_media_urls_sets_media_url_none(monkeypatch):  # texto puro → media_url None (sin romper)
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", lambda c, p: "acc-1")
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00", "platform": "instagram"}))
    assert rows["r"][0]["media_url"] is None
