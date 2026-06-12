"""P0-2 · gate X5 brand voice draft->scheduled (ritual G3 · falla primero).

Verifica el contrato del gate `check_or_raise` con el scorer y la cache/audit
mockeados (cero DB / cero LLM real · G9 exime tests). check_or_raise retorna
brand_voice_skipped (bool) y lanza 422/503 segun corresponda:
  - score < 0.7              -> HTTPException 422 brand_voice_below_threshold:cid=score,...
  - score >= 0.7             -> retorna False (no skip) + persiste el score
  - force + score < 0.7      -> retorna + audita el override (agent_memory)
  - scorer caido (Result err)-> HTTPException 503 con la valvula force_brand_voice
  - CACHE (refinamiento 5): 2do agendado del mismo contenido SIN edicion
    (scored_at >= updated_at) -> CERO llamadas al scorer
  - SIN referencia de marca (corpus vacio · 11 jun): PASS con rastro -> retorna
    True (skipped) + record_skip en agent_memory + CERO calls al scorer/adapter
"""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch

from fastapi import HTTPException

from app.api.routes.calendar_v3 import _brand_voice_gate as g


def _row(cid, *, text="hola marca", score=None, scored_at=None,
         updated_at="2026-06-10T00:00:00+00:00"):
    return {"id": cid, "generated_text": text, "brand_voice_score": score,
            "brand_voice_scored_at": scored_at, "updated_at": updated_at}


def _run(content_ids, *, rows, score_result, force=False, has_reference=True):
    """Corre check_or_raise con scorer + cache + audit + has_brand_reference
    mockeados. Devuelve (skipped_bool, contadores)."""
    calls = {"score": 0, "persist": [], "audit": [], "skip": []}

    async def _fake_score(client_id, text):
        calls["score"] += 1
        return score_result

    with ExitStack() as s:
        s.enter_context(patch.object(g, "has_brand_reference", lambda cid: has_reference))
        s.enter_context(patch.object(g.cache, "fetch_scorables", return_value=rows))
        s.enter_context(patch.object(g.cache, "persist_score",
                                     lambda cid, sc: calls["persist"].append((cid, sc))))
        s.enter_context(patch.object(g.cache, "record_override",
                                     lambda *a, **k: calls["audit"].append((a, k))))
        s.enter_context(patch.object(g.cache, "record_skip",
                                     lambda *a, **k: calls["skip"].append((a, k))))
        s.enter_context(patch.object(g, "score_brand_voice", _fake_score))
        out = asyncio.run(g.check_or_raise("u1", "cli-A", content_ids, force))
    return out, calls


def _expect_http(content_ids, code, *, rows, score_result, force=False):
    try:
        _run(content_ids, rows=rows, score_result=score_result, force=force)
        assert False, f"esperaba HTTPException {code}"
    except HTTPException as e:
        assert e.status_code == code
        return e


def test_below_threshold_422_lista_cuales_fallaron():
    rows = {"c1": _row("c1", score=None), "c2": _row("c2", score=None)}
    e = _expect_http(["c1", "c2"], 422, rows=rows, score_result=(True, {"score": 0.42, "reasons": []}, None))
    assert e.detail.startswith("brand_voice_below_threshold:")
    assert "c1=0.42" in e.detail and "c2=0.42" in e.detail


def test_above_threshold_pasa_y_persiste_score():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.88, "reasons": []}, None))
    assert out is False                       # no skip
    assert calls["persist"] == [("c1", 0.88)]
    assert calls["audit"] == [] and calls["skip"] == []


def test_force_bajo_umbral_pasa_y_audita():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.30, "reasons": ["off-tone"]}, None), force=True)
    assert out is False
    assert len(calls["audit"]) == 1


def test_scorer_caido_503_con_valvula_de_escape():
    rows = {"c1": _row("c1", score=None)}
    e = _expect_http(["c1"], 503, rows=rows, score_result=(False, None, "brand_voice_check_unavailable"))
    assert "brand_voice_check_unavailable" in e.detail
    assert "force_brand_voice=true" in e.detail


def test_scorer_caido_con_force_agenda_bajo_responsabilidad():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(False, None, "brand_voice_check_unavailable"), force=True)
    assert out is False
    assert len(calls["audit"]) == 1


def test_cache_fresco_reusa_score_sin_llamar_al_scorer():
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T01:00:00+00:00",
                       updated_at="2026-06-10T00:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.10, "reasons": []}, None))
    assert out is False
    assert calls["score"] == 0
    assert calls["persist"] == []


def test_cache_stale_por_edicion_recalcula():
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T00:00:00+00:00",
                       updated_at="2026-06-10T02:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.80, "reasons": []}, None))
    assert out is False
    assert calls["score"] == 1
    assert calls["persist"] == [("c1", 0.80)]


def test_sin_referencia_de_marca_pasa_con_rastro_sin_haiku():
    # cliente sin voz de marca definida → PASS con rastro · score NULL (no se
    # persiste) · agent_memory registra el skip · CERO calls al scorer (11 jun)
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1", "c2"], rows=rows,
                      score_result=(True, {"score": 0.10, "reasons": []}, None),
                      has_reference=False)
    assert out is True                        # brand_voice_skipped
    assert calls["score"] == 0                # no se gasto Haiku
    assert calls["persist"] == []             # score queda NULL
    assert len(calls["skip"]) == 1            # rastro en agent_memory
