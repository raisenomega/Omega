"""Selector del publish_fn de REX · lee REX_LIVE_ENABLED y decide real vs shadow (DEBT-098).

Capa worker (composición · puede importar api). Mantiene el UC flag-agnóstico: el UC solo
recibe la fn. DEFAULT OFF → shadow (REX INERTE en prod · NO llama publish_scheduled_post).
El log distingue ambos por published_at (shadow=NULL · live-éxito=timestamp).
"""
import logging
from typing import Optional

from app.bc_cognition.application.rex_publish_uc import PublishFn
from app.bc_cognition.infrastructure import rex_publish_repository as repo
from app.api.routes.publishing._publish_service import publish_scheduled_post, PublishGateError

logger = logging.getLogger(__name__)


async def _shadow_publish(post_id: str, client_id: str) -> tuple[bool, Optional[str]]:
    """REX_LIVE_ENABLED OFF · NO publica · solo registra la intención (shadow_mode)."""
    return False, "shadow_mode"


async def _live_publish(post_id: str, client_id: str) -> tuple[bool, Optional[str]]:
    """REX_LIVE_ENABLED ON · publica de verdad · traduce gate/fallo a (ok, reason)."""
    try:
        res = await publish_scheduled_post(post_id, client_id)
        return res.published, (None if res.published else f"publish_failed:{res.error}")
    except PublishGateError as e:
        return False, f"publish_gate:{e.code}"


def select_publish_fn() -> PublishFn:
    """OFF (default) → shadow (inerte) · ON → real. Garantía de inercia de REX en prod."""
    live = repo.rex_live_enabled()
    logger.info(f"rex publish_fn = {'LIVE' if live else 'shadow'} (REX_LIVE_ENABLED)")
    return _live_publish if live else _shadow_publish
