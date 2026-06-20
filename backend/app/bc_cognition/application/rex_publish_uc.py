"""Use case REX · orquesta la publicación autónoma por cliente (DEBT-098 · F2).

Por cada due post: arma el gate input, evalúa rex_gate, registra el outcome.
  - hold → log + memory, sigue al siguiente.
  - publish + REX_LIVE_ENABLED OFF → log 'publish' SIN publicar (shadow · post queda pending).
  - publish + REX_LIVE_ENABLED ON → publish_scheduled_post (lock: max_instances=1 del cron
    + mark_publishing sobre 'pending' · decisión A · no pre-reclamar este incremento).
Fail-safe: gating ilegible → skip cliente (incluye crisis) · señales ilegibles → el gate
holdea (None/0). El aislamiento por negocio lo hereda de publish_scheduled_post.
"""
import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from app.bc_cognition.application import _rex_steps as steps
from app.bc_cognition.domain.rex_gate import evaluate_rex_gate
from app.bc_cognition.infrastructure import rex_publish_repository as repo
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_DUE_LIMIT = 10

# Inyectada por el worker (Fase 4) · (post_id, client_id) -> (publicado, reason|None).
# Mantiene application SIN depender de api/ (publish_scheduled_post vive en la capa api).
PublishFn = Callable[[str, str], Awaitable[tuple[bool, Optional[str]]]]


async def run_rex_for_client(client_id: str, publish_fn: PublishFn) -> dict[str, Any]:
    """Recorre los due posts del cliente · fail-safe (nunca propaga al scheduler)."""
    gating = await asyncio.to_thread(repo.fetch_client_gating, client_id)
    if not gating:  # fail-safe: sin gating legible NO se evalúa (cubre crisis ilegible)
        return {"client_id": client_id, "skipped": "gating_unreadable"}
    if not (gating.get("rex_addon_active") and gating.get("autonomous_mode_on")):
        return {"client_id": client_id, "skipped": "gating_off"}

    # UC flag-agnóstico: NO lee REX_LIVE_ENABLED. Para cada decisión 'publish' llama a
    # publish_fn (la inyecta el wrapper · OFF=shadow no-op → (False,'shadow_mode') sin
    # publicar · ON=real → publish_scheduled_post). El registro distingue ambos por published_at.
    sb = get_supabase_service()
    due = await asyncio.to_thread(repo.fetch_due_posts, client_id, _DUE_LIMIT)
    # Conteo POR RED (anti-spam por red · cada red su cupo · ver rex_gate check 5).
    published_by_platform = await asyncio.to_thread(repo.count_published_today_by_platform, client_id)
    holds = published = 0

    for post in due:
        content = await asyncio.to_thread(repo.fetch_content_signals, str(post.get("content_id") or ""))
        account = await asyncio.to_thread(repo.fetch_account_binding, str(post.get("social_account_id") or ""))
        platform = str(account.get("platform") or "")
        ctx = steps.build_gate_input(post, content, account, gating, published_by_platform.get(platform, 0))
        verdict = evaluate_rex_gate(ctx)

        if verdict.decision == "hold":
            await asyncio.to_thread(steps.record_outcome, sb, post, gating, client_id,
                                    "hold", verdict.reason, False, platform, ctx.brand_voice_score)
            holds += 1
            continue

        ok, reason = await publish_fn(str(post.get("id") or ""), client_id)
        await asyncio.to_thread(steps.record_outcome, sb, post, gating, client_id,
                                "publish", reason, ok, platform, ctx.brand_voice_score)
        if ok:
            published += 1
            # incremento POR RED dentro de la corrida (no combinado)
            published_by_platform[platform] = published_by_platform.get(platform, 0) + 1

    return {"client_id": client_id, "due": len(due), "published": published, "holds": holds}
