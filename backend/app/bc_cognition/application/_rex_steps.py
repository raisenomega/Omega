"""Helpers del use case REX (DDD · UC delgado). Arma el gate input desde las filas
ya leídas y registra el outcome (rex_publish_log + agent_memory). I/O sync."""
from datetime import datetime, timezone
from typing import Any, Optional

from app.bc_cognition.domain.rex_gate import RexGateInput
from app.bc_cognition.infrastructure import rex_publish_repository as repo
from app.bc_cognition.infrastructure import aria_memory_repository as mem
from app.infrastructure.supabase_service import SupabaseService

# Espejo de _publish_service: solo estas redes exigen PRESENCIA de media.
_MEDIA_REQUIRED = {"instagram", "tiktok"}


def build_gate_input(post: dict[str, Any], content: dict[str, Any],
                     account: dict[str, Any], gating: dict[str, Any],
                     posts_today: int) -> RexGateInput:
    """Ensambla el input del gate · fail-safe: señal ausente → None/0 → el gate holdea."""
    platform = str(account.get("platform") or "")
    bv = content.get("brand_voice_score")
    return RexGateInput(
        addon_active=bool(gating.get("rex_addon_active")),
        toggle_on=bool(gating.get("autonomous_mode_on")),
        crisis_active=bool(gating.get("crisis_active")),
        brand_voice_score=float(bv) if bv is not None else None,
        confidence=int(content.get("confidence") or 0),
        posts_today=posts_today,
        has_media=(bool(post.get("media_url")) if platform in _MEDIA_REQUIRED else True),
        connection_valid=bool(account.get("zernio_account_id")),
    )


def record_outcome(sb: SupabaseService, post: dict[str, Any], gating: dict[str, Any],
                   client_id: str, gate_result: str, reason: Optional[str],
                   published: bool, platform: Optional[str], bv_score: Optional[float]) -> None:
    """Escribe rex_publish_log + agent_memory (agent_code='rex_publisher' · was_correct=None → F3)."""
    now = datetime.now(timezone.utc).isoformat()
    repo.insert_rex_publish_log({
        "client_id": client_id,
        "scheduled_post_id": post.get("id"),
        "platform": platform,
        "published_at": now if published else None,
        "scheduled_for": post.get("scheduled_for"),
        "gate_result": gate_result,
        "hold_reason": reason,
        "brand_voice_score": bv_score,
    })
    uid = gating.get("user_id")
    if uid:
        mem.insert_agent_memory(
            sb, str(uid), client_id, gating.get("reseller_id"),
            user_message=f"rex:scheduled_post:{post.get('id')}",
            assistant_response=f"{gate_result}:{reason or 'ok'}",
            level=0, source_event_id=None, was_correct=None,
            content_id=post.get("content_id"), agent_code="rex_publisher",
        )
