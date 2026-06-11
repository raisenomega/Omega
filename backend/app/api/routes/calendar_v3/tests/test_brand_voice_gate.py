"""P0-2 · gate X5 brand voice draft->scheduled (ritual G3 · falla primero).

Verifica el contrato del gate `check_or_raise` con el scorer y la cache/audit
mockeados (cero DB / cero LLM real · G9 exime tests):
  - score < 0.7              -> HTTPException 422 brand_voice_below_threshold:cid=score,...
  - score >= 0.7             -> retorna {cid: score} + persiste el score
  - force + score < 0.7      -> retorna + audita el override (agent_memory)
  - scorer caido (Result err)-> HTTPException 503 con la valvula de escape force_brand_voice
  - CACHE (refinamiento 5): 2do agendado del mismo contenido SIN edicion
    (scored_at >= updated_at) -> CERO llamadas al scorer (assert sobre el mock)
  - cache stale (editado tras scoring · updated_at > scored_at) -> re-calcula
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


def _run(content_ids, *, rows, score_result, force=False):
    """Corre check_or_raise con scorer + cache + audit mockeados.
    Devuelve (salida, contadores). score_result = (ok, val, err) del scorer."""
    calls = {"score": 0, "persist": [], "audit": []}

    async def _fake_score(client_id, text):
        calls["score"] += 1
        return score_result

    with ExitStack() as s:
        s.enter_context(patch.object(g.cache, "fetch_scorables", return_value=rows))
        s.enter_context(patch.object(g.cache, "persist_score",
                                     lambda cid, sc: calls["persist"].append((cid, sc))))
        s.enter_context(patch.object(g.cache, "record_override",
                                     lambda *a, **k: calls["audit"].append((a, k))))
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
    # ambos por debajo · el detail debe nombrar cada content_id con su score (Ajuste 1)
    e = _expect_http(["c1", "c2"], 422, rows=rows, score_result=(True, {"score": 0.42, "reasons": []}, None))
    assert e.detail.startswith("brand_voice_below_threshold:")
    assert "c1=0.42" in e.detail and "c2=0.42" in e.detail


def test_above_threshold_pasa_y_persiste_score():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.88, "reasons": []}, None))
    assert out == {"c1": 0.88}
    assert calls["persist"] == [("c1", 0.88)]
    assert calls["audit"] == []


def test_force_bajo_umbral_pasa_y_audita():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.30, "reasons": ["off-tone"]}, None), force=True)
    assert out == {"c1": 0.30}
    assert len(calls["audit"]) == 1  # override humano queda registrado


def test_scorer_caido_503_con_valvula_de_escape():
    rows = {"c1": _row("c1", score=None)}
    e = _expect_http(["c1"], 503, rows=rows, score_result=(False, None, "brand_voice_check_unavailable"))
    assert "brand_voice_check_unavailable" in e.detail
    assert "force_brand_voice=true" in e.detail  # el outage NO paraliza la agencia


def test_scorer_caido_con_force_agenda_bajo_responsabilidad():
    rows = {"c1": _row("c1", score=None)}
    out, calls = _run(["c1"], rows=rows, score_result=(False, None, "brand_voice_check_unavailable"), force=True)
    assert len(calls["audit"]) == 1
    assert "c1" not in out or out == {}  # sin score real · pero no se inventa (cero-mocks)


def test_cache_fresco_reusa_score_sin_llamar_al_scorer():
    # scored_at >= updated_at Y score no-null → fresco → CERO LLM (refinamiento 5)
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T01:00:00+00:00",
                       updated_at="2026-06-10T00:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.10, "reasons": []}, None))
    assert out == {"c1": 0.91}
    assert calls["score"] == 0          # NO se pago Haiku
    assert calls["persist"] == []       # no re-persiste


def test_cache_stale_por_edicion_recalcula():
    # updated_at > scored_at → el contenido se edito tras el scoring → stale → re-score
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T00:00:00+00:00",
                       updated_at="2026-06-10T02:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.80, "reasons": []}, None))
    assert out == {"c1": 0.80}
    assert calls["score"] == 1
    assert calls["persist"] == [("c1", 0.80)]
