"""Commit 5b · puntúa el guion del carrusel al GENERAR (paridad caption) · la respuesta trae virality_score
+ virality_estimated + brand_dna_score → la tarjeta pinta los chips. Reusa build_dna_for_client +
compute_virality_score (NO duplica el scorer). Best-effort: si el scoring falla, render igual (score 0).
Mock al seam: build_dna_for_client + compute_virality_score en _carousel_score. G9 exime tests."""
import asyncio
from types import SimpleNamespace

from app.api.routes.content_lab_v3.handlers import carousel_render as cr
from app.api.routes.content_lab_v3 import _carousel_score as cscore
from app.api.routes.content_lab_v3.models.content_lab_models import (
    CarouselSlide, GenerateCarouselRenderRequest,
)
from app.bc_cognition.domain.input_threats import SanitizerAction


async def _user(auth): return {"id": "u1"}


def _req(n=5):
    s = [CarouselSlide(order=i, slide_type="punto", text=f"placa {i}", visual_note=f"bg {i}") for i in range(n)]
    return GenerateCarouselRenderRequest(carousel_title="5 ventajas", slides=s, client_id="c1")


def _wire(monkeypatch, *, dna_score=0.73, virality=64, score_raises=False):
    cap = {"virality_text": None}

    async def _budget(cid, n, route="default"): return True
    async def _brand(cid): return ", paleta"
    def _san(text, ctx): return SimpleNamespace(action=SanitizerAction.ALLOW, clean_text=text), None
    async def _gen(prompts, client_id=None, size="1024x1280", **k):
        return [f"https://s/{i}.png" for i in range(len(prompts))]
    async def _ins(label, fn, client_id, payload): return "content1"
    async def _debit(cid, agent, cost, model=None, eid=None): pass
    def _build_dna(client_id, vertical=None):
        if score_raises:
            raise RuntimeError("dna boom")
        return SimpleNamespace(score=dna_score)
    def _virality(text, dna, platform):
        cap["virality_text"] = text
        return {"score": virality, "breakdown": {}, "estimated": True}

    monkeypatch.setattr(cr, "get_current_user", _user)
    monkeypatch.setattr(cr, "resolve_client_or_403", lambda uid, cid: {"id": "c1"})
    monkeypatch.setattr(cr, "check_budget_for_n", _budget)
    monkeypatch.setattr(cr, "fetch_brand_block", _brand)
    monkeypatch.setattr(cr, "sanitize_input", _san)
    monkeypatch.setattr(cr, "generate_carousel_images", _gen)
    monkeypatch.setattr(cr.repo, "safe_insert", _ins)
    monkeypatch.setattr(cr, "debit", _debit)
    monkeypatch.setattr(cscore.use_brand_dna, "build_dna_for_client", _build_dna)
    monkeypatch.setattr(cscore, "compute_virality_score", _virality)
    return cap


def test_carousel_render_puntua(monkeypatch):
    _wire(monkeypatch, dna_score=0.73, virality=64)
    out = asyncio.run(cr.carousel_render(_req(5), None))
    assert out.virality_score == 64 and out.virality_estimated is True
    assert out.brand_dna_score == 0.73


def test_virality_sobre_guion(monkeypatch):
    cap = _wire(monkeypatch)
    asyncio.run(cr.carousel_render(_req(3), None))
    txt = cap["virality_text"]
    assert "5 ventajas" in txt                 # el título
    for i in range(3):
        assert f"placa {i}" in txt             # cada placa del guion (NO sobre vacío)


def test_brand_dna_del_cliente(monkeypatch):
    _wire(monkeypatch, dna_score=0.42)
    out = asyncio.run(cr.carousel_render(_req(5), None))
    assert out.brand_dna_score == 0.42         # = dna.score del cliente


def test_cliente_dna_vacio(monkeypatch):
    _wire(monkeypatch, dna_score=0.0, virality=12)
    out = asyncio.run(cr.carousel_render(_req(5), None))
    assert out.brand_dna_score == 0.0          # corpus vacío → sin chip de voz (como el caption)
    assert out.virality_score == 12            # el virality igual se calcula


def test_scoring_falla_no_tumba(monkeypatch):
    _wire(monkeypatch, score_raises=True)      # build_dna lanza → best-effort
    out = asyncio.run(cr.carousel_render(_req(5), None))
    assert out.content_type == "carousel"
    assert out.media_urls == [f"https://s/{i}.png" for i in range(5)]  # el carrusel se devuelve igual
    assert out.virality_score == 0 and out.brand_dna_score == 0.0      # sin chips, NO 500
