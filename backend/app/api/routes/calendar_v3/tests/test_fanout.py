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
        "client-A", ["instagram", "facebook"], ["c1"], _TS, None, resolve=_accounts({}))
    assert rows == []  # handler -> 422 (error claro · 0 rows)


def test_single_network_one_row_backcompat():
    rows = _fanout.build_fanout_rows(
        "client-A", ["instagram"], ["c1"], _TS, None, resolve=_accounts({"instagram": "ig-1"}))
    assert len(rows) == 1 and rows[0]["social_account_id"] == "ig-1"  # single-red no se rompio


# ─── "AMBAS" · placement feed/story/both → _fanout emite 1-2 filas por red ───
@pytest.mark.parametrize("placement,plats,mapping,expected_is_story", [
    ("feed", ["instagram"], {"instagram": "ig-1"}, [False]),        # feed → 1 fila normal
    ("story", ["instagram"], {"instagram": "ig-1"}, [True]),        # story → 1 fila historia
    ("both", ["instagram"], {"instagram": "ig-1"}, [False, True]),  # both IG → feed + story
    ("both", ["tiktok"], {"tiktok": "tk-1"}, [False]),              # both TikTok → solo feed (sin historia)
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


# both multi-red: cada red con historia emite [feed,story]; TikTok solo feed; red sin cuenta → 0 filas (invariante E).
@pytest.mark.parametrize("plats,mapping,expected", [
    (["instagram", "facebook"], {"instagram": "ig-1", "facebook": "fb-1"}, {"ig-1": [False, True], "fb-1": [False, True]}),
    (["instagram", "tiktok"], {"instagram": "ig-1", "tiktok": "tk-1"}, {"ig-1": [False, True], "tk-1": [False]}),
    (["instagram", "facebook"], {"instagram": "ig-1"}, {"ig-1": [False, True]}),  # fb sin cuenta → omitido por completo
])
def test_placement_both_multired(plats, mapping, expected):
    rows = _fanout.build_fanout_rows("client-A", plats, ["c1"], _TS, None,
                                     resolve=_accounts(mapping), placement="both")
    assert {r["social_account_id"] for r in rows} == set(expected)  # solo redes resueltas (jamas NULL)
    for acc, exp in expected.items():
        assert sorted(r["is_story"] for r in rows if r["social_account_id"] == acc) == exp


# ─── Pieza 2 capa 3 · carrusel · media_urls (array) + doble-escritura media_url=array[0] (caso F · sin IndexError) ───
# Contrato: row["media_urls"]=array si presente else None · row["media_url"]=array[0] si presente else single legacy.
@pytest.mark.parametrize("media_urls,plats,mapping,placement,exp_urls,exp_url,exp_n", [
    (["u1", "u2", "u3"], ["instagram"], {"instagram": "ig-1"}, "feed", ["u1", "u2", "u3"], "u1", 1),  # array → fila
    (None, ["instagram"], {"instagram": "ig-1"}, "feed", None, "u1", 1),                              # None → single legacy
    (["u1", "u2"], ["instagram", "facebook"], {"instagram": "ig-1", "facebook": "fb-1"}, "both", ["u1", "u2"], "u1", 4),  # replica N×red×placement
    ([], ["instagram"], {"instagram": "ig-1"}, "feed", None, "u1", 1),                                # [] → fallback single
])
def test_media_urls_doble_escritura(media_urls, plats, mapping, placement, exp_urls, exp_url, exp_n):
    rows = _fanout.build_fanout_rows("client-A", plats, ["c1"], _TS, "u1",
                                     resolve=_accounts(mapping), placement=placement, media_urls=media_urls)
    assert len(rows) == exp_n
    assert all(r["media_urls"] == exp_urls and r["media_url"] == exp_url for r in rows)
