"""Pieza 1 · A2.4 · puente: guion → N prompts → A2.2 → 1 draft con media_urls + débito. Todo mockeado
(A2.2/A2.3/A2.1/sanitize/repo/debit). Prueba ensamblado, todo-o-nada extremo-a-extremo, débito N×costo,
sanitización. G9 exime tests."""
import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes.content_lab_v3.handlers import carousel_render as cr
from app.api.routes.content_lab_v3.models.content_lab_models import (
    CarouselSlide, GenerateCarouselRenderRequest,
)
from app.bc_cognition.domain.input_threats import SanitizerAction


async def _user(auth): return {"id": "u1"}


def _req(n=5, title="Tips"):
    s = [CarouselSlide(order=i, slide_type="punto", text=f"texto {i}", visual_note=f"dark bg {i}") for i in range(n)]
    return GenerateCarouselRenderRequest(carousel_title=title, slides=s, client_id="c1")


def _common(monkeypatch, budget_ok=True, gen_raises=False, cap=None):
    h = {"san": 0, "ins": None, "ins_called": False, "costs": []}

    async def _budget(cid, n, route="default"): return budget_ok
    async def _brand(cid): return ", brand color palette: use #00fa3e as primary"

    def _san(text, ctx):
        h["san"] += 1
        return SimpleNamespace(action=SanitizerAction.ALLOW, clean_text=text), None

    async def _gen(prompts, client_id=None, size="1024x1280", **k):
        if cap is not None: cap.update(prompts=prompts, size=size)
        if gen_raises: raise RuntimeError("Nano Banana generation failed: api_error · boom")
        return [f"https://s/{i}.png" for i in range(len(prompts))]

    async def _ins(label, fn, client_id, payload):
        h["ins_called"] = True; h["ins"] = payload; return "content1"

    async def _debit(cid, agent, cost, model=None, eid=None): h["costs"].append(cost)

    monkeypatch.setattr(cr, "get_current_user", _user)
    monkeypatch.setattr(cr, "resolve_client_or_403", lambda uid, cid: {"id": "c1"})
    monkeypatch.setattr(cr, "check_budget_for_n", _budget)
    monkeypatch.setattr(cr, "fetch_brand_block", _brand)
    monkeypatch.setattr(cr, "sanitize_input", _san)
    monkeypatch.setattr(cr, "generate_carousel_images", _gen)
    monkeypatch.setattr(cr.repo, "safe_insert", _ins)
    monkeypatch.setattr(cr, "debit", _debit)
    return h


def test_render_N_placas_1_draft(monkeypatch):
    h = _common(monkeypatch)
    out = asyncio.run(cr.carousel_render(_req(5), None))
    p = h["ins"]
    assert p["content_type"] == "carousel" and p["generated_text"] == "Tips"
    assert p["media_urls"] == [f"https://s/{i}.png" for i in range(5)]
    assert len(p["metadata"]["slides"]) == 5
    assert out.media_urls == p["media_urls"] and out.content_type == "carousel"


def test_budget_bloquea_temprano(monkeypatch):
    cap: dict = {}
    h = _common(monkeypatch, budget_ok=False, cap=cap)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(cr.carousel_render(_req(6), None))
    assert ei.value.status_code == 402 and "prompts" not in cap
    assert h["ins_called"] is False and h["costs"] == []


def test_todo_o_nada_no_persist(monkeypatch):
    h = _common(monkeypatch, gen_raises=True)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(cr.carousel_render(_req(6), None))
    assert ei.value.status_code == 503 and h["ins_called"] is False and h["costs"] == []


def test_debito_N_por_costo(monkeypatch):
    from app.bc_billing.domain.credit_costs import cost_for_image
    h = _common(monkeypatch)
    asyncio.run(cr.carousel_render(_req(5), None))
    assert h["costs"] == [pytest.approx(5 * cost_for_image("default"))]  # un solo débito = N×costo
