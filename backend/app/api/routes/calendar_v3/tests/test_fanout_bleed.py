"""Fix del BLEED · _fanout escribe el media SOLO en la fila de la pieza dueña (media_content_id) ·
el caption/otras piezas del MISMO bloque quedan SIN media. Espeja test_fanout (resolver inyectado · cero DB).
Antes: media_urls (array) se replicaba idéntico a TODA fila → un caption salía con las placas del carrusel."""
from datetime import datetime, timezone

from app.api.routes.calendar_v3 import _fanout

_TS2 = [datetime(2026, 6, 1, 15, 0, tzinfo=timezone.utc),
        datetime(2026, 6, 1, 17, 0, tzinfo=timezone.utc)]
_TS1 = [datetime(2026, 6, 1, 15, 0, tzinfo=timezone.utc)]


def _ig(client_id, platform):
    return "ig-1"


def _by_cid(rows):
    return {r["content_id"]: r for r in rows}


def test_bleed_caption_no_recibe_placas():
    # bloque [caption, carrusel] · las placas pertenecen al carrusel · el caption queda SIN media (cierra el bleed)
    rows = _fanout.build_fanout_rows(
        "cli", ["instagram"], ["cap", "carr"], _TS2, "p1",
        resolve=_ig, media_urls=["p1", "p2", "p3"], media_content_id="carr")
    by = _by_cid(rows)
    assert by["carr"]["media_urls"] == ["p1", "p2", "p3"] and by["carr"]["media_url"] == "p1"
    assert by["cap"]["media_urls"] is None and by["cap"]["media_url"] is None


def test_carrusel_solo():
    # bloque de SOLO un carrusel · su fila lleva las N placas + media_url=placa[0] (doble-escritura)
    rows = _fanout.build_fanout_rows(
        "cli", ["instagram"], ["carr"], _TS1, "p1",
        resolve=_ig, media_urls=["p1", "p2"], media_content_id="carr")
    assert len(rows) == 1
    assert rows[0]["media_urls"] == ["p1", "p2"] and rows[0]["media_url"] == "p1"


def test_dos_carruseles():
    # el request lleva UN array de media (el de la pieza dueña) · solo esa pieza lo recibe · la otra queda sin media
    rows = _fanout.build_fanout_rows(
        "cli", ["instagram"], ["carrA", "carrB"], _TS2, "a1",
        resolve=_ig, media_urls=["a1", "a2"], media_content_id="carrA")
    by = _by_cid(rows)
    assert by["carrA"]["media_urls"] == ["a1", "a2"] and by["carrA"]["media_url"] == "a1"
    assert by["carrB"]["media_urls"] is None and by["carrB"]["media_url"] is None


def test_solo_texto():
    # sin media en el bloque · ninguna fila lleva media (ni array ni single)
    rows = _fanout.build_fanout_rows(
        "cli", ["instagram"], ["cap"], _TS1, None, resolve=_ig)
    assert rows[0]["media_urls"] is None and rows[0]["media_url"] is None


def test_imagen_suelta():
    # imagen suelta (single legacy · sin media_content_id) → se adjunta a su caption · retrocompat intacta
    rows = _fanout.build_fanout_rows(
        "cli", ["instagram"], ["cap"], _TS1, "https://m/x.jpg", resolve=_ig)
    assert rows[0]["media_url"] == "https://m/x.jpg" and rows[0]["media_urls"] is None
