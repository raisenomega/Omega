"""Repository ARIA · contexto VIVO del plan del cliente (FASE 0b · DDD A1/A9).

Split de aria_repository por C4 (cierra DEBT-051 · mismo patrón que aria_memory_repository).

SEGURIDAD G5: ARIA corre con service_role (bypassa RLS) → el aislamiento NO viene de RLS,
viene del patrón de query. CADA query filtra .eq("client_id", client_id) con el client_id
derivado server-side en _resolve_role (nunca de input del usuario).
PRIVACIDAD: stripe_subscription_id / customer / tarjeta NO se seleccionan (ni se traen).
"""
from typing import Any
from app.infrastructure.supabase_service import SupabaseService

# Posts/mes por plan · ⚠️ COPIA MANUAL de src/lib/plan-limits.ts (PLAN_CONFIGS.postsPerCycle).
# Fuente de verdad = frontend · si cambian allá, actualizar acá. No hay import TS→Python.
_PLAN_POST_LIMITS = {"adopcion": 7, "basic": 32, "pro": 64, "enterprise": 192}


def fetch_live_plan(supabase: SupabaseService, client_id: str, ctx: dict[str, Any]) -> None:
    """Añade a ctx: _plan (plan + renovación + addons · SIN stripe_id) · _posts_used · _credits.
    Best-effort: lo envuelve el try del caller · si falla, ARIA sigue sin el dato (P1)."""
    pl = supabase.client.table("client_plans").select(
        "plan, current_period_start, current_period_end, addons"
    ).eq("client_id", client_id).limit(1).execute()
    ctx["_plan"] = pl.data[0] if pl.data else None

    # posts usados en el periodo actual (límite vive en domain · PLAN_POST_LIMITS)
    start = ctx["_plan"].get("current_period_start") if ctx["_plan"] else None
    pq = supabase.client.table("content_lab_generated").select("id", count="exact").eq("client_id", client_id)
    if start:
        pq = pq.gte("created_at", start)
    ctx["_posts_used"] = pq.execute().count or 0
    plan_code = (ctx["_plan"] or {}).get("plan")
    ctx["_posts_limit"] = _PLAN_POST_LIMITS.get(plan_code) if plan_code else None

    cr = supabase.client.table("client_agent_credits").select(
        "packs, budget_usd_mensual, consumido_usd, periodo_end"
    ).eq("client_id", client_id).limit(1).execute()
    ctx["_credits"] = cr.data[0] if cr.data else None
    ctx["_plan_block"] = _format_plan_block(ctx)


def _format_plan_block(ctx: dict[str, Any]) -> str:
    """Bloque 'TU PLAN' para el prompt. Renovación = fecha SIN monto (decisión owner · sin stripe_id).
    Campo ausente → no se afirma (P1). '' si no hay plan."""
    pl = ctx.get("_plan")
    if not pl:
        return ""
    used, lim = ctx.get("_posts_used"), ctx.get("_posts_limit")
    posts = f" · {used}/{lim} posts usados ({lim - used} restantes)" if isinstance(lim, int) and isinstance(used, int) else ""
    renew = f" · se renueva el {str(pl.get('current_period_end'))[:10]}" if pl.get("current_period_end") else ""
    extras = ", ".join(str(x) for x in (list(pl.get("addons") or []) + list((ctx.get("_credits") or {}).get("packs") or [])) if x)
    return f"# TU PLAN\nPlan {pl.get('plan')}{posts}{renew}" + (f" · add-ons activos: {extras}" if extras else "")
