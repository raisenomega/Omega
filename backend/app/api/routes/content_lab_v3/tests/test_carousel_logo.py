"""Commit A · logo opt-in en el carrusel (paridad con imagen suelta) · overlay best-effort por placa.
Reusa overlay_logo/upload (de imagen suelta · NO los toca). Mock al seam: overlay/upload en _carousel_logo
+ find_client_logo_url en repo. Prueba: true→N overlays, false→0, sin-logo→sin error, falla-una→best-effort.
G9 exime tests."""
import asyncio
from types import SimpleNamespace

from app.api.routes.content_lab_v3.handlers import carousel_render as cr
from app.api.routes.content_lab_v3 import _carousel_logo as clogo
from app.api.routes.content_lab_v3.models.content_lab_models import (
    CarouselSlide, GenerateCarouselRenderRequest,
)
from app.bc_cognition.domain.input_threats import SanitizerAction


async def _user(auth): return {"id": "u1"}


def _req(n=5, apply_logo=True):
    s = [CarouselSlide(order=i, slide_type="punto", text=f"texto {i}", visual_note=f"bg {i}") for i in range(n)]
    return GenerateCarouselRenderRequest(carousel_title="Tips", slides=s, client_id="c1", apply_logo=apply_logo)


def _wire(monkeypatch, *, logo_url="https://s/logo.png", fail_url=None):
    h = {"ins": None, "overlay": [], "upload": 0}

    async def _budget(cid, n, route="default"): return True
    async def _brand(cid): return ", paleta"
    def _san(text, ctx): return SimpleNamespace(action=SanitizerAction.ALLOW, clean_text=text), None
    async def _gen(prompts, client_id=None, size="1024x1280", **k):
        return [f"https://s/{i}.png" for i in range(len(prompts))]
    async def _ins(label, fn, client_id, payload): h["ins"] = payload; return "content1"
    async def _debit(cid, agent, cost, model=None, eid=None): pass
    def _find_logo(cid): return logo_url
    def _overlay(image_url, lurl):
        h["overlay"].append(image_url)
        if fail_url is not None and image_url == fail_url:
            raise RuntimeError("overlay boom")
        return image_url.encode()  # bytes que codifican la url origen (determinístico · rastreable)
    async def _upload(image_bytes, mime, client_id=None):
        h["upload"] += 1
        return "logo+" + image_bytes.decode()

    monkeypatch.setattr(cr, "get_current_user", _user)
    monkeypatch.setattr(cr, "resolve_client_or_403", lambda uid, cid: {"id": "c1"})
    monkeypatch.setattr(cr, "check_budget_for_n", _budget)
    monkeypatch.setattr(cr, "fetch_brand_block", _brand)
    monkeypatch.setattr(cr, "sanitize_input", _san)
    monkeypatch.setattr(cr, "generate_carousel_images", _gen)
    monkeypatch.setattr(cr.repo, "safe_insert", _ins)
    monkeypatch.setattr(cr, "debit", _debit)
    monkeypatch.setattr(cr.repo, "find_client_logo_url", _find_logo)
    monkeypatch.setattr(clogo, "overlay_logo", _overlay)
    monkeypatch.setattr(clogo, "upload_image_bytes", _upload)
    return h


def test_apply_logo_true(monkeypatch):
    h = _wire(monkeypatch)
    out = asyncio.run(cr.carousel_render(_req(5, apply_logo=True), None))
    assert len(h["overlay"]) == 5  # 1 overlay por placa
    expected = [f"logo+https://s/{i}.png" for i in range(5)]
    assert h["ins"]["media_urls"] == expected  # urls reemplazadas por las overlaid (mismo orden)
    assert out.media_urls == expected


def test_apply_logo_false(monkeypatch):
    h = _wire(monkeypatch)
    out = asyncio.run(cr.carousel_render(_req(5, apply_logo=False), None))
    assert h["overlay"] == []  # overlay NUNCA llamado
    original = [f"https://s/{i}.png" for i in range(5)]
    assert h["ins"]["media_urls"] == original and out.media_urls == original  # intactas (como hoy)


def test_sin_logo_cliente(monkeypatch):
    h = _wire(monkeypatch, logo_url=None)  # cliente sin logo cargado
    out = asyncio.run(cr.carousel_render(_req(5, apply_logo=True), None))
    assert h["overlay"] == []  # sin logo → sin overlay, sin error
    original = [f"https://s/{i}.png" for i in range(5)]
    assert h["ins"]["media_urls"] == original and out.media_urls == original  # render completo


def test_overlay_falla_una_placa(monkeypatch):
    h = _wire(monkeypatch, fail_url="https://s/2.png")  # el overlay de la placa 2 lanza
    out = asyncio.run(cr.carousel_render(_req(5, apply_logo=True), None))
    assert len(h["overlay"]) == 5  # se intentó en las 5 (best-effort)
    got = h["ins"]["media_urls"]
    assert got[2] == "https://s/2.png"  # la que falló queda con su url original (sin logo)
    for i in (0, 1, 3, 4):
        assert got[i] == f"logo+https://s/{i}.png"  # las demás overlaid · NO 500 · carrusel completo
    assert out.media_urls == got
