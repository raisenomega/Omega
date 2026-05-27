"""DEBT-100 · worker del cron decision_evaluator (ARIA_LEARNING_LOOP §9).

Capa fina sobre bc_cognition/application/evaluate_decisions · alinea el cron con el
arbol workers/ del spec y aisla el registro en main.py del use case. Cada hora (:30).
"""
import logging
from app.bc_cognition.application.evaluate_decisions import run_decision_evaluation

logger = logging.getLogger(__name__)


async def run_decision_evaluator_job() -> dict[str, int]:
    """Entry-point del cron · ejecuta la evaluacion y loguea el resumen.
    Fail-safe: run_decision_evaluation captura sus errores internamente · el cron
    nunca se rompe (no propaga excepciones al scheduler)."""
    stats = await run_decision_evaluation()
    logger.info(f"decision_evaluator_worker · resumen={stats}")
    return stats
