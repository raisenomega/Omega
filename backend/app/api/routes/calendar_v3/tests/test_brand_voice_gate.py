"""X5 · gate brand voice draft->scheduled · DAMAGE GATE de 2 bandas (11 jun).

check_or_raise retorna {"skipped": bool, "below_brand_bar": bool} y:
  - score < 0.5 (SCORE_BLOCK_THRESHOLD)  -> 422 brand_voice_damages_brand:cid=score
    (DAÑA la marca: insultos/spam/off-tone)
  - 0.5 <= score < 0.7 (SCORE_BRAND_BAR) -> PASA + below_brand_bar=True + persiste
  - score >= 0.7                         -> PASA limpio + persiste
  - force => agenda + audita el override (agent_memory)
  - scorer caido (Result err)            -> 503 con valvula force_brand_voice
  - CACHE: 2do agendado sin edicion       -> CERO calls al scorer
  - SIN referencia de marca               -> skipped=True + record_skip + 0 calls
  - pieza no-texto (image/video)          -> skip con rastro · el bloque no falla
Todo con scorer + cache + audit + has_brand_reference mockeados (G9 exime tests).
"""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch

from fastapi import HTTPException

from app.api.routes.calendar_v3 import _brand_voice_gate as g


def _row(cid, *, text="hola marca", score=None, scored_at=None,
         updated_at="2026-06-10T00:00:00+00:00", content_type="text"):
    return {"id": cid, "content_type": content_type, "generated_text": text,
            "brand_voice_score": score, "brand_voice_scored_at": scored_at,
            "updated_at": updated_at}


def _run(content_ids, *, rows, score_result, force=False, has_reference=True):
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


def test_dana_la_marca_422_lista_cuales():
    rows = {"c1": _row("c1"), "c2": _row("c2")}
    e = _expect_http(["c1", "c2"], 422, rows=rows, score_result=(True, {"score": 0.15, "reasons": []}, None))
    assert e.detail.startswith("brand_voice_damages_brand:")
    assert "c1=0.15" in e.detail and "c2=0.15" in e.detail


def test_on_brand_pasa_limpio_sin_flag():
    rows = {"c1": _row("c1")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.88, "reasons": []}, None))
    assert out == {"skipped": False, "below_brand_bar": False}
    assert calls["persist"] == [("c1", 0.88)]


def test_generico_05_07_pasa_con_below_brand_bar():
    # neutro/genérico: no daña → PASA, pero marca below_brand_bar (refinamiento owner)
    rows = {"c1": _row("c1")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.62, "reasons": []}, None))
    assert out == {"skipped": False, "below_brand_bar": True}
    assert calls["persist"] == [("c1", 0.62)]   # score persistido (no inventado)
    assert calls["audit"] == []                  # no es override · solo flag


def test_frontera_05_no_dana():
    rows = {"c1": _row("c1")}
    out, _ = _run(["c1"], rows=rows, score_result=(True, {"score": 0.50, "reasons": []}, None))
    assert out["below_brand_bar"] is True        # 0.50 pasa con flag (no 422)


def test_force_dana_pasa_y_audita():
    rows = {"c1": _row("c1")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.10, "reasons": ["insultos"]}, None), force=True)
    assert out["skipped"] is False
    assert len(calls["audit"]) == 1


def test_scorer_caido_503_con_valvula():
    rows = {"c1": _row("c1")}
    e = _expect_http(["c1"], 503, rows=rows, score_result=(False, None, "brand_voice_check_unavailable"))
    assert "force_brand_voice=true" in e.detail


def test_scorer_caido_con_force_audita():
    rows = {"c1": _row("c1")}
    out, calls = _run(["c1"], rows=rows, score_result=(False, None, "brand_voice_check_unavailable"), force=True)
    assert len(calls["audit"]) == 1


def test_cache_fresco_reusa_sin_scorer():
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T01:00:00+00:00",
                       updated_at="2026-06-10T00:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.10, "reasons": []}, None))
    assert out == {"skipped": False, "below_brand_bar": False}
    assert calls["score"] == 0 and calls["persist"] == []


def test_cache_stale_recalcula():
    rows = {"c1": _row("c1", score=0.91,
                       scored_at="2026-06-10T00:00:00+00:00",
                       updated_at="2026-06-10T02:00:00+00:00")}
    out, calls = _run(["c1"], rows=rows, score_result=(True, {"score": 0.80, "reasons": []}, None))
    assert calls["score"] == 1 and calls["persist"] == [("c1", 0.80)]


def test_pieza_no_texto_skip_sin_fallar():
    rows = {"cap": _row("cap"), "img": _row("img", content_type="image", text="")}
    out, calls = _run(["cap", "img"], rows=rows, score_result=(True, {"score": 0.88, "reasons": []}, None))
    assert out["skipped"] is False
    assert calls["score"] == 1 and calls["persist"] == [("cap", 0.88)]
    assert len(calls["skip"]) == 1


def test_sin_referencia_skip_con_rastro():
    rows = {"c1": _row("c1")}
    out, calls = _run(["c1", "c2"], rows=rows,
                      score_result=(True, {"score": 0.10, "reasons": []}, None), has_reference=False)
    assert out == {"skipped": True, "below_brand_bar": False}
    assert calls["score"] == 0 and len(calls["skip"]) == 1
