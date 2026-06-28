"""Opción A · el gate de agendar PUNTÚA el guion del carrusel (título+placas) en vez de saltarlo (era score=NULL
→ REX holdeaba por siempre). Score real → REX publica si ≥0.7, retiene si <0.7. image/video siguen skip. G9 exime."""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch

from app.api.routes.calendar_v3 import _brand_voice_gate as g
from app.bc_cognition.domain.rex_gate import RexGateInput, evaluate_rex_gate

_UPD = "2026-06-28T00:00:00+00:00"


def _carousel_row(cid, *, title="5 ventajas", slides=None):
    return {"id": cid, "content_type": "carousel", "generated_text": title,
            "metadata": {"slides": slides or [{"text": "placa uno"}, {"text": "placa dos"}, {"text": "placa tres"}]},
            "brand_voice_score": None, "brand_voice_scored_at": None, "updated_at": _UPD}


def _text_row(cid, text="caption normal de marca", content_type="text"):
    return {"id": cid, "content_type": content_type, "generated_text": text,
            "metadata": None, "brand_voice_score": None, "brand_voice_scored_at": None, "updated_at": _UPD}


def _run(content_ids, *, rows, score_result, force=False, has_reference=True):
    calls = {"score": 0, "text": [], "persist": [], "skip": []}

    async def _fake_score(client_id, text):
        calls["score"] += 1
        calls["text"].append(text)
        return score_result

    with ExitStack() as s:
        s.enter_context(patch.object(g, "has_brand_reference", lambda cid: has_reference))
        s.enter_context(patch.object(g.cache, "fetch_scorables", return_value=rows))
        s.enter_context(patch.object(g.cache, "persist_score",
                                     lambda cid, sc: calls["persist"].append((cid, sc))))
        s.enter_context(patch.object(g.cache, "record_override", lambda *a, **k: None))
        s.enter_context(patch.object(g.cache, "record_skip",
                                     lambda *a, **k: calls["skip"].append((a, k))))
        s.enter_context(patch.object(g, "score_brand_voice", _fake_score))
        out = asyncio.run(g.check_or_raise("u1", "cli-A", content_ids, force))
    return out, calls


def _rex_would(score):  # REX con ese score: publish si ≥0.7, hold si <0.7 (los otros 6 checks en verde)
    ctx = RexGateInput(addon_active=True, toggle_on=True, crisis_active=False, brand_voice_score=score,
                       confidence=8, posts_today_platform=0, has_media=True, connection_valid=True)
    return evaluate_rex_gate(ctx).decision


def test_carrusel_se_puntua():
    out, calls = _run(["c1"], rows={"c1": _carousel_row("c1")},
                      score_result=(True, {"score": 0.85, "reasons": []}, None))
    assert calls["score"] == 1                  # ya NO se salta · se puntúa
    assert calls["persist"] == [("c1", 0.85)]   # score real escrito (ya no NULL)
    assert len(calls["skip"]) == 0              # no fue a la rama non_text
    assert out["skipped"] is False


def test_concat_guion():
    slides = [{"text": "Razon uno proteccion"}, {"text": "Razon dos notificaciones"}, {"text": "CTA buzon"}]
    _, calls = _run(["c1"], rows={"c1": _carousel_row("c1", title="5 ventajas Mail Boxes", slides=slides)},
                    score_result=(True, {"score": 0.85, "reasons": []}, None))
    scored = calls["text"][0]
    assert "5 ventajas Mail Boxes" in scored               # el título
    for sl in slides:
        assert sl["text"] in scored                        # cada placa del guion
    assert len(scored) > len("5 ventajas Mail Boxes")      # NO solo el título corto


def test_carrusel_buen_guion_pasa():
    _, calls = _run(["c1"], rows={"c1": _carousel_row("c1")},
                    score_result=(True, {"score": 0.85, "reasons": []}, None))
    assert calls["persist"] == [("c1", 0.85)]
    assert _rex_would(0.85) == "publish"        # score real ≥0.7 → REX publica


def test_carrusel_mal_guion_retiene():
    out, calls = _run(["c1"], rows={"c1": _carousel_row("c1")},
                      score_result=(True, {"score": 0.60, "reasons": []}, None))
    assert calls["persist"] == [("c1", 0.60)]   # score real escrito
    assert out["below_brand_bar"] is True       # pasa agendar con flag (0.5–0.7)
    assert _rex_would(0.60) == "hold"           # pero REX lo retiene (P2 · <0.7 · razón legítima)


def test_no_rompe_texto_normal():
    _, calls = _run(["t1"], rows={"t1": _text_row("t1")},
                    score_result=(True, {"score": 0.9, "reasons": []}, None))
    assert calls["text"] == ["caption normal de marca"]   # puntúa el generated_text tal cual (sin guion)
    assert calls["persist"] == [("t1", 0.9)]
    assert len(calls["skip"]) == 0


def test_otros_non_text_siguen_saltando():
    rows = {"img": _text_row("img", text="", content_type="image"),
            "vid": _text_row("vid", text="", content_type="video")}
    _, calls = _run(["img", "vid"], rows=rows, score_result=(True, {"score": 0.9, "reasons": []}, None))
    assert calls["score"] == 0          # ninguno se puntúa (no tienen copy)
    assert calls["persist"] == []
    assert len(calls["skip"]) == 1      # ambos a record_skip (1 llamada con la lista)
