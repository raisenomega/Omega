"""E · tests del fan-out multi-red del bloque Content Lab (build_fanout_rows · funcion pura).

Espeja test_supervised_approve.py: resolver de cuenta INYECTADO (_accounts(mapping)) + assert sobre
las rows construidas. Cero DB real. Producto cruzado N items de texto x M redes resueltas.
INVARIANTE: jamas una row con social_account_id NULL · red sin cuenta active -> omitida.
"""
import pytest
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


# ─── "AMBAS" · placement feed/story/both → _fanout emite 1-2 filas por red ───
@pytest.mark.parametrize("placement,plats,mapping,expected_is_story", [
    ("feed", ["instagram"], {"instagram": "ig-1"}, [False]),                 # feed → 1 fila normal
    ("story", ["instagram"], {"instagram": "ig-1"}, [True]),                 # story → 1 fila historia
    ("both", ["instagram"], {"instagram": "ig-1"}, [False, True]),           # both IG/FB → feed + story
    ("both", ["tiktok"], {"tiktok": "tk-1"}, [False]),                       # both TikTok → solo feed (sin historia)
])
def test_placement_single_network_rows(placement, plats, mapping, expected_is_story):
    rows = _fanout.build_fanout_rows("client-A", plats, ["c1"], _TS, None,
                                     resolve=_accounts(mapping), placement=placement)
    assert [r["is_story"] for r in rows] == expected_is_story  # feed primero, luego story


def test_placement_default_no_kwarg_one_feed_row():
    """Sin placement (default 'feed') → 1 fila is_story=false · flujo de hoy intacto."""
    rows = _fanout.build_fanout_rows("client-A", ["instagram"], ["c1"], _TS, None,
                                     resolve=_accounts({"instagram": "ig-1"}))
    assert len(rows) == 1 and rows[0]["is_story"] is False


def test_placement_both_ig_fb_four_rows():
    """IG+FB ambas → 4 publicaciones (feed+story por red que soporta story)."""
    rows = _fanout.build_fanout_rows("client-A", ["instagram", "facebook"], ["c1"], _TS, None,
                                     resolve=_accounts({"instagram": "ig-1", "facebook": "fb-1"}), placement="both")
    assert len(rows) == 4
    assert sorted(r["is_story"] for r in rows if r["social_account_id"] == "ig-1") == [False, True]
    assert sorted(r["is_story"] for r in rows if r["social_account_id"] == "fb-1") == [False, True]


def test_placement_both_ig_tiktok_three_rows():
    """IG (feed+story) + TikTok (solo feed) = 3 filas."""
    rows = _fanout.build_fanout_rows("client-A", ["instagram", "tiktok"], ["c1"], _TS, None,
                                     resolve=_accounts({"instagram": "ig-1", "tiktok": "tk-1"}), placement="both")
    assert len(rows) == 3
    assert sorted(r["is_story"] for r in rows if r["social_account_id"] == "ig-1") == [False, True]
    assert [r["is_story"] for r in rows if r["social_account_id"] == "tk-1"] == [False]


def test_placement_both_network_without_account_zero_rows_invariant():
    """Invariante E intacto en 'both': red sin cuenta active → 0 filas de esa red (ni feed ni story)."""
    rows = _fanout.build_fanout_rows("client-A", ["instagram", "facebook"], ["c1"], _TS, None,
                                     resolve=_accounts({"instagram": "ig-1"}), placement="both")  # fb no resuelve
    assert {r["social_account_id"] for r in rows} == {"ig-1"}  # fb omitido por completo
    assert all(r["social_account_id"] is not None for r in rows)
