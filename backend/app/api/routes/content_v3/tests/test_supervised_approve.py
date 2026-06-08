"""P2 · tests del puente aprobar->calendario (maybe_schedule_on_approve · FAN-OUT por red).
Mock de cal_repo (insert) + _first_active_account_id. Cero DB real. G9 exime tests.
Contrato: 1 row por red marcada (metadata.platforms) con su social_account_id resuelto ·
ninguna red resuelta -> NO agenda (falta_red, queda approved) · B2 (sin fecha -> no agenda) · supervisado-only.
INVARIANTE: jamas se inserta un pending con social_account_id NULL (cierra sin_red de raiz)."""
from unittest.mock import MagicMock
from app.api.routes.content_v3 import _supervised_approve as sa


def _item(metadata, cid="draft-1", client="client-A"):
    return {"id": cid, "client_id": client, "metadata": metadata, "generated_text": "post"}


def _accounts(mapping):
    return lambda c, p: mapping.get(p)


def test_fanout_one_row_per_marked_network(monkeypatch):
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({"instagram": "ig-1", "facebook": "fb-1"}))
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00",
                                              "platforms": ["instagram", "facebook"]}))
    assert out["scheduled"] is True and out["falta_red"] is False and out["scheduled_for"] == "2026-06-01T15:00"
    inserted = rows["r"]
    assert len(inserted) == 2
    assert {row["social_account_id"] for row in inserted} == {"ig-1", "fb-1"}
    assert all(row["status"] == "pending" and row["social_account_id"] is not None for row in inserted)
    assert all(row["content_id"] == "draft-1" and row["scheduled_for"] == "2026-06-01T15:00" for row in inserted)


def test_backcompat_single_platform_string(monkeypatch):
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({"instagram": "ig-1"}))
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00",
                                              "platform": "instagram"}))
    assert out["scheduled"] is True and len(rows["r"]) == 1 and rows["r"][0]["social_account_id"] == "ig-1"


def test_general_without_networks_does_not_schedule(monkeypatch):  # raiz del sin_red
    called = MagicMock()
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({}))
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-02T00:00:00-04:00",
                                              "platform": "general"}))
    assert out["scheduled"] is False and out["falta_red"] is True
    called.assert_not_called()  # NUNCA un pending con social_account_id NULL


def test_marked_network_without_active_account_skipped(monkeypatch):
    called = MagicMock()
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({}))  # ninguna resuelve
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00",
                                              "platforms": ["instagram"]}))
    assert out["scheduled"] is False and out["falta_red"] is True
    called.assert_not_called()


def test_partial_resolution_schedules_only_resolved(monkeypatch):
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({"facebook": "fb-1"}))  # ig no resuelve
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00",
                                              "platforms": ["instagram", "facebook"]}))
    assert out["scheduled"] is True and len(rows["r"]) == 1 and rows["r"][0]["social_account_id"] == "fb-1"


def test_supervised_without_date_does_not_schedule(monkeypatch):  # B2
    called = MagicMock()
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"supervisado": True, "platforms": ["instagram"]}))  # sin fecha
    assert out is None
    called.assert_not_called()  # queda approved · cliente agenda manual


def test_non_supervised_draft_ignored(monkeypatch):
    called = MagicMock()
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", called)
    out = sa.maybe_schedule_on_approve(_item({"fecha_sugerida": "2026-06-01T15:00", "platforms": ["instagram"]}))
    assert out is None
    called.assert_not_called()


def test_media_urls_propagates_across_fanout(monkeypatch):  # foto adjunta -> publisher (cada red)
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({"instagram": "ig-1", "facebook": "fb-1"}))
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    item = {**_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00", "platforms": ["instagram", "facebook"]}),
            "media_urls": ["https://media/x.jpg"]}
    sa.maybe_schedule_on_approve(item)
    assert all(row["media_url"] == "https://media/x.jpg" for row in rows["r"])


def test_no_media_urls_sets_media_url_none(monkeypatch):  # texto puro -> media_url None (sin romper)
    rows = {}
    monkeypatch.setattr(sa, "_first_active_account_id", _accounts({"instagram": "ig-1"}))
    monkeypatch.setattr(sa.cal_repo, "insert_scheduled_posts_bulk", lambda r: rows.update(r=r) or r)
    sa.maybe_schedule_on_approve(_item({"supervisado": True, "fecha_sugerida": "2026-06-01T15:00",
                                        "platforms": ["instagram"]}))
    assert rows["r"][0]["media_url"] is None
