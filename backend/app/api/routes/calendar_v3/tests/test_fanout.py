"""E · tests del fan-out multi-red del bloque Content Lab (build_fanout_rows · funcion pura).

Espeja test_supervised_approve.py: resolver de cuenta INYECTADO (_accounts(mapping)) + assert sobre
las rows construidas. Cero DB real. Producto cruzado N items de texto x M redes resueltas.
INVARIANTE: jamas una row con social_account_id NULL · red sin cuenta active -> omitida.
"""
from datetime import datetime, timezone
from app.api.routes.calendar_v3 import _fanout


_TS = [datetime(2026, 6, 1, 15, 0, tzinfo=timezone.utc)]  # N=1 (1 caption · caso tipico)


def _accounts(mapping):
    return lambda c, p: mapping.get(p)


def test_three_networks_all_active_three_rows():
    rows = _fanout.build_fanout_rows(
        "client-A", ["instagram", "facebook", "tiktok"], ["c1"], _TS, "https://m/x.jpg",
        resolve=_accounts({"instagram": "ig-1", "facebook": "fb-1", "tiktok": "tk-1"}))
    assert len(rows) == 3
    assert {r["social_account_id"] for r in rows} == {"ig-1", "fb-1", "tk-1"}
    assert all(r["status"] == "pending" and r["social_account_id"] is not None for r in rows)
    assert all(r["content_id"] == "c1" and r["client_id"] == "client-A" for r in rows)


def test_one_network_without_active_account_skipped_two_rows():
    rows = _fanout.build_fanout_rows(
        "client-A", ["instagram", "facebook", "tiktok"], ["c1"], _TS, None,
        resolve=_accounts({"instagram": "ig-1", "facebook": "fb-1"}))  # tiktok no resuelve
    assert len(rows) == 2
    assert {r["social_account_id"] for r in rows} == {"ig-1", "fb-1"}  # invariante: tiktok omitido


def test_zero_networks_resolve_no_rows():
    rows = _fanout.build_fanout_rows(
        "client-A", ["instagram", "facebook"], ["c1"], _TS, None,
        resolve=_accounts({}))  # ninguna resuelve
    assert rows == []  # handler -> 422 (error claro · 0 rows)


def test_single_network_one_row_backcompat():
    rows = _fanout.build_fanout_rows(
        "client-A", ["instagram"], ["c1"], _TS, None,
        resolve=_accounts({"instagram": "ig-1"}))
    assert len(rows) == 1 and rows[0]["social_account_id"] == "ig-1"  # single-red no se rompio
