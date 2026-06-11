"""IO del gate X5 · cache del score + persistencia + audit del override.

cache (refinamiento 1): el score vive en content_lab_generated.brand_voice_score
+ brand_voice_scored_at. Fresco si scored_at >= updated_at (no editado tras el
scoring). persist vía RPC mark_brand_voice_scored (now() estable por transacción
== updated_at del trigger 00001 → el write NO se auto-invalida). audit del
override humano → agent_memory (M1 · tabla existente · sin tabla nueva · P5)."""
import json
import logging
from datetime import datetime
from typing import Any

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_COLS = "id, generated_text, brand_voice_score, brand_voice_scored_at, updated_at"


def _sb():
    return get_supabase_service().client


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch_scorables(client_id: str, content_ids: list[str]) -> dict[str, dict[str, Any]]:
    """Filas de content_lab_generated (del client) por id · para puntuar/cachear."""
    if not content_ids:
        return {}
    r = _sb().table("content_lab_generated").select(_COLS).eq(
        "client_id", client_id).in_("id", content_ids).execute()
    return {str(row["id"]): row for row in (r.data or [])}


def is_fresh(row: dict[str, Any]) -> bool:
    """Score vigente: existe Y se calculó en o después del último cambio del contenido."""
    score = row.get("brand_voice_score")
    scored_at, updated_at = row.get("brand_voice_scored_at"), row.get("updated_at")
    if score is None or not scored_at or not updated_at:
        return False
    try:
        return _parse_ts(scored_at) >= _parse_ts(updated_at)
    except ValueError:
        return False


def persist_score(content_id: str, score: float) -> None:
    """RPC atómica: score + scored_at=now() en una transacción (scored_at ==
    updated_at del trigger → cache hit recién escrito · solo invalida al editar)."""
    _sb().rpc("mark_brand_voice_scored",
              {"p_content_id": content_id, "p_score": score}).execute()


def record_override(user_id: str, client_id: str,
                    failures: dict[str, float], unavailable: list[str]) -> None:
    """Override humano del gate → agent_memory (decisión auditada · P5)."""
    _sb().table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id,
        "agent_code": "brand_voice_checker", "memory_type": "episodic",
        "context": "schedule force override · brand_voice gate X5",
        "decision": "brand_voice_override_forced",
        "reasoning": json.dumps({"below_threshold": failures, "unavailable": unavailable}),
        "confidence": 7, "was_correct": None,
    }).execute()
