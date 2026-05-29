"""Modo Supervisado (DEBT-097) · máquina de estados de aprobación.

ARIA genera draft -> PARA -> cliente aprueba/rechaza. Esta capa decide QUÉ draft
entra a la cola de revisión (gates P2/P3 de limits_omega) y lista los pendientes.

NO toca limits_omega.py · solo importa LIMITS_OMEGA + is_action_prohibited.
Aprobar NO vive aquí: el front reusa PATCH /content/{id}/save (aprendizaje ya cableado).
Reject delega en content_v3._content_repository.update_status.

DEBT-096 (cron strategy_generator) será OTRA fuente de drafts que use enqueue_for_review.
"""
from typing import Any, Optional

from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA, is_action_prohibited

_SUPERVISADO_FLAG = "supervisado"


def should_enqueue(draft: dict[str, Any], requires_approval: bool) -> bool:
    """P2/P3 gate · True si el draft debe ir a la cola supervisada (no se publica solo).

    - requires_approval: client_context.requires_publish_approval (default True).
    - P3: confidence >= MIN_CONFIDENCE_TO_ACT (drafts bajo el umbral no se proponen).
    - P2: agent_code prohibido (crisis/etc.) NUNCA entra al flujo automático -> hold humano.
    """
    if not requires_approval:
        return False
    agent_code = str(draft.get("agent_code") or "")
    if is_action_prohibited(agent_code) or agent_code == "crisis_manager":
        return False
    confidence = draft.get("confidence")
    if not isinstance(confidence, (int, float)):
        return False
    return confidence >= LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"]


def mark_supervisado(metadata: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Devuelve metadata con el flag supervisado=true (no muta el original)."""
    base = dict(metadata or {})
    base[_SUPERVISADO_FLAG] = True
    return base


def is_supervisado(draft: dict[str, Any]) -> bool:
    """True si el draft fue marcado para revisión supervisada."""
    meta = draft.get("metadata")
    return bool(isinstance(meta, dict) and meta.get(_SUPERVISADO_FLAG) is True)


def filter_pending(drafts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """De una lista de content_lab_generated, deja solo los supervisados en status=draft."""
    return [d for d in drafts if d.get("status") == "draft" and is_supervisado(d)]
