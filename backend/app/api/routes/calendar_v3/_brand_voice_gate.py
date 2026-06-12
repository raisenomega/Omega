"""Gate X5 · brand voice draft->scheduled (P2 con dientes · auditoría 10 jun 2026).

Ningún content_id pasa a scheduled con match_score < 0.7 (X5). Reusa score
cacheado vigente (refinamiento 1 · cero LLM) · si no, lo calcula en vivo vía
score_brand_voice (Haiku · I2/I10). Outage del scorer → 503 honesto con válvula
force_brand_voice (refinamiento 2). force => agenda + audita el override (P1)."""
import logging
from fastapi import HTTPException

from app.api.routes.calendar_v3 import _brand_voice_cache as cache
from app.bc_cognition.application.score_brand_voice import score_brand_voice, has_brand_reference
from app.bc_cognition.domain.brand_voice_scorer_prompt import (
    SCORE_BLOCK_THRESHOLD, SCORE_BRAND_BAR,
)

logger = logging.getLogger(__name__)

_UNAVAILABLE_DETAIL = (
    "brand_voice_check_unavailable · usa force_brand_voice=true para agendar "
    "bajo responsabilidad humana (queda auditado)"
)
_NON_TEXT_TYPES = {"image", "video", "carousel"}  # sin copy que scorear · skip con rastro


async def check_or_raise(user_id: str, client_id: str,
                         content_ids: list[str], force: bool) -> dict:
    """Damage gate X5 · retorna {"skipped": bool, "below_brand_bar": bool}.
    422 solo si algún score DAÑA la marca (<0.5) · 0.5–0.7 pasa con flag · ≥0.7
    limpio · 503 si el scorer cae (válvula force_brand_voice)."""
    # Sin referencia de marca → no se puede medir desviación de una voz indefinida.
    # PASS con rastro (score NULL, no inventado) · determinístico, antes de Haiku.
    if not has_brand_reference(client_id):
        cache.record_skip(user_id, client_id, content_ids)
        return {"skipped": True, "below_brand_bar": False}

    rows = cache.fetch_scorables(client_id, content_ids)
    scores: dict[str, float] = {}
    unavailable: list[str] = []
    non_text: list[str] = []
    for cid in content_ids:
        row = rows.get(cid)
        if row and row.get("content_type") in _NON_TEXT_TYPES:
            non_text.append(cid)   # imagen/video/carousel · no tiene copy → skip
            continue
        if row and cache.is_fresh(row):
            scores[cid] = float(row["brand_voice_score"])
            continue
        ok, val, _err = await score_brand_voice(client_id, (row or {}).get("generated_text") or "")
        if not ok:
            if not force:
                raise HTTPException(503, _UNAVAILABLE_DETAIL)
            unavailable.append(cid)
            continue
        scores[cid] = val["score"]
        cache.persist_score(cid, val["score"])

    if non_text:
        cache.record_skip(user_id, client_id, non_text, reason="x5_skip_non_text_content")
    damaging = {c: s for c, s in scores.items() if s < SCORE_BLOCK_THRESHOLD}
    below_bar = any(SCORE_BLOCK_THRESHOLD <= s < SCORE_BRAND_BAR for s in scores.values())
    if damaging and not force:
        detail = "brand_voice_damages_brand:" + ",".join(
            f"{c}={s:.2f}" for c, s in damaging.items())
        raise HTTPException(422, detail)
    if (damaging or unavailable) and force:
        cache.record_override(user_id, client_id, damaging, unavailable)
    return {"skipped": False, "below_brand_bar": below_bar}
