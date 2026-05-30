"""Use case: generación ON-DEMAND de una estrategia de contenido (DEBT-096 Fase 1).

REUSA el pipeline de ARIA (resolve_role + fetch_aria_context + build_client_context_block +
fetch_web_context + load_and_format_memory + generate) · NO recopia su lógica · una sola fuente.
Brave as-is (genérico · DEBT-BRAVE-CONTEXTO aparte). tipo='manual' (Fase 2 cron usará cadence_for).
"""
from typing import Optional
from app.bc_cognition.application._aria_memory_context import load_and_format_memory
from app.bc_cognition.application.web_context import fetch_web_context
from app.bc_cognition.domain.client_context_block import build_client_context_block
from app.bc_cognition.domain.strategy_prompt import build_strategy_system, parse_strategy
from app.bc_cognition.infrastructure import aria_repository as repo, strategy_repository as strat
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError
from app.infrastructure.supabase_service import get_supabase_service

_QUERY = "estrategia de contenido y tendencias del nicho"


class StrategyResult:
    def __init__(self, id: Optional[str], titulo: str, contenido: dict) -> None:
        self.id = id
        self.titulo = titulo
        self.contenido = contenido


async def use_generate_strategy(
    client_id: str, reseller_id: Optional[str] = None,
    tipo: str = "manual", generation_key: Optional[str] = None,
) -> tuple[Optional[StrategyResult], Optional[ClaudeError]]:
    """Genera y persiste una estrategia activa para el cliente. (result, err). El handler resuelve
    el rol y gatea budget ANTES (check_budget · 402) · acá solo generación pura."""
    supabase = get_supabase_service()
    # Reuso del pipeline de ARIA · cada bloque se LLAMA, no se reconstruye.
    ctx = repo.fetch_aria_context(supabase, client_id)
    ctx_block = build_client_context_block(ctx) if ctx else ""
    vertical = (ctx.get("vertical") or ctx.get("niche") or "") if ctx else ""
    web_block = await fetch_web_context(_QUERY, vertical, "strategy", client_id)
    memory_block = load_and_format_memory(supabase, client_id, reseller_id, query=_QUERY)
    system = build_strategy_system(ctx_block, web_block, memory_block)

    resp, err = await generate(
        "strategy", system,
        [{"role": "user", "content": "Generá la estrategia para este periodo ahora."}],
        max_tokens=1500,
    )
    if err or resp is None:
        return None, err or ClaudeError("unknown", "La generación de estrategia no devolvió respuesta.")
    parsed = parse_strategy(resp.text)
    if not parsed:
        return None, ClaudeError("parse_error", "ARIA no devolvió una estrategia válida. Probá de nuevo.")

    sid = await repo.safe_insert("strategy_insert", strat.insert_strategy,
                                 supabase, client_id, parsed["titulo"], parsed["contenido"], tipo, generation_key)
    return StrategyResult(id=sid, titulo=parsed["titulo"], contenido=parsed["contenido"]), None
