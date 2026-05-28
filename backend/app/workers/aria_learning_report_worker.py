"""Cron worker · ARIA Learning Report semanal (DEBT-101 · lunes 07:05 UTC).

Llama use case + brief_dispatcher.dispatch_aria_learning_brief. Si no hay actividad
(sin clientes con decisions_total>0) → dispatch retorna False y el worker no rompe.
Best-effort: cualquier excepción → log + return (cron sigue vivo).
"""
import logging

from app.bc_cognition.application.aria_learning_report import get_weekly_report
from app.bc_cognition.application.brief_dispatcher import dispatch_aria_learning_brief

logger = logging.getLogger(__name__)


async def run() -> None:
    """Entry point del cron · best-effort · log + return si fallo."""
    try:
        report = get_weekly_report()
    except Exception as e:
        logger.error(f"aria_learning_report.get fallo: {e}", exc_info=True)
        return
    try:
        sent = await dispatch_aria_learning_brief(report)
        if not sent:
            logger.info("aria_learning_report: sin actividad esta semana · skip email")
    except Exception as e:
        logger.error(f"aria_learning_report.dispatch fallo: {e}", exc_info=True)
