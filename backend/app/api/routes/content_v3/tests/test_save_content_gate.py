"""Gap supervisado (11 jun) · el approve supervisado pasa por el gate X5.

Antes, draft->approved (dispara corpus + agendado fan-out) NO consultaba el
damage gate → contenido que DAÑA la marca se colaba por la puerta del Modo
Supervisado, salteándose el filtro. Ahora check_or_raise corre ANTES de
cualquier side-effect: daño → 422 y NADA cambia (ni status, ni corpus, ni schedule)."""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch, AsyncMock

from fastapi import HTTPException

from app.api.routes.content_v3.handlers import save_content as h
from app.api.routes.content_v3.models.content_models import SaveContentRequest

_DRAFT = {"id": "d1", "client_id": "cli-A", "status": "draft", "generated_text": "post"}


def _item(ui_type=None):
    """Draft con metadata.ui_type (el tipo fino · el corpus solo aprende de 'caption')."""
    it = {"id": "d1", "client_id": "cli-A", "status": "draft", "generated_text": "post"}
    if ui_type is not None:
        it["metadata"] = {"ui_type": ui_type}
    return it


def _run(is_saved, *, item=None, gate_raises=False):
    item = item if item is not None else dict(_DRAFT)
    calls = {"safe_insert": [], "gate": 0}
    raised = {"code": None}

    async def _gate(user_id, client_id, content_ids, force):
        calls["gate"] += 1
        if gate_raises:
            raise HTTPException(422, "brand_voice_damages_brand:d1=0.15")
        return {"skipped": False, "below_brand_bar": False}

    async def _safe_insert(label, fn, *a, **k):
        calls["safe_insert"].append(label)
        return {"scheduled": False}

    with ExitStack() as s:
        s.enter_context(patch.object(h, "get_current_user", AsyncMock(return_value={"id": "u1"})))
        s.enter_context(patch.object(h.reader, "get_content_item", return_value=item))
        s.enter_context(patch.object(h.reader, "get_accessible_client_ids", return_value=["cli-A"]))
        s.enter_context(patch.object(h.brand_gate, "check_or_raise", _gate))
        s.enter_context(patch.object(h.repo, "safe_insert", _safe_insert))
        try:
            asyncio.run(h.save_content("d1", SaveContentRequest(is_saved=is_saved), "Bearer x"))
        except HTTPException as e:
            raised["code"] = e.status_code
    return calls, raised["code"]


def test_approve_danino_422_no_cambia_nada():
    calls, code = _run(True, gate_raises=True)
    assert code == 422
    assert calls["gate"] == 1
    assert calls["safe_insert"] == []   # el gate corrió ANTES · cero side-effects (status/corpus/schedule)


def test_approve_ok_procede_y_aprende():
    calls, code = _run(True, item=_item("caption"), gate_raises=False)
    assert code is None and calls["gate"] == 1
    assert "update_status" in calls["safe_insert"] and "corpus" in calls["safe_insert"]


def test_unapprove_no_corre_gate():
    calls, code = _run(False)   # approved->draft (is_saved=false) · no se gatea des-aprobar
    assert code is None and calls["gate"] == 0


# ── Corpus solo-caption (B · la raíz · solo metadata.ui_type=='caption' aprende voz de marca) ──
def test_approve_caption_entra_al_corpus():
    calls, code = _run(True, item=_item("caption"))
    assert code is None and "corpus" in calls["safe_insert"]   # caption SÍ aprende


def test_approve_video_script_no_entra_al_corpus():
    calls, code = _run(True, item=_item("video_script"))
    assert code is None
    assert "corpus" not in calls["safe_insert"]                # script NO contamina la referencia
    assert "update_status" in calls["safe_insert"]             # aprobar/agendar intactos
    assert "memory" in calls["safe_insert"]                    # memory NO se gatea (solo el corpus)


def test_approve_hashtags_no_entra_al_corpus():
    calls, code = _run(True, item=_item("hashtags"))
    assert code is None and "corpus" not in calls["safe_insert"]


def test_approve_sin_uitype_no_entra_al_corpus():
    calls, code = _run(True, item=_item(None))                 # metadata vacío → fail-closed
    assert code is None and "corpus" not in calls["safe_insert"]
