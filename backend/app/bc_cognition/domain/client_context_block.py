"""Bloque de contexto del cliente para ARIA (TAREA C · dominio puro · A2).

Inyectado en cada mensaje: negocio, audiencia, objetivos, voz de marca, cuentas
conectadas y documento subido. Cap total 2000 (I6) · uploaded cede espacio primero.
"""
from typing import Any

_TOTAL_CAP = 2000
_UPLOADED_CAP = 1500


def _joined(ctx: dict[str, Any], keys: tuple[str, ...]) -> str:
    return " · ".join(str(ctx[k]).replace(",", ", ") for k in keys if ctx.get(k))


def _accounts_line(accounts: list[dict[str, Any]]) -> str:
    shown = ", ".join(
        f"{a.get('platform')} @{a.get('account_name')}"
        for a in accounts[:6] if a.get("platform") and a.get("account_name")
    )
    return f"Cuentas conectadas: {shown}" if shown else "Cuentas conectadas: ninguna aún."


def build_client_context_block(ctx: dict[str, Any]) -> str:
    """Bloque real del cliente para ARIA · total ≤2000 chars (uploaded capado)."""
    lines: list[str] = []
    niche = ctx.get("niche") or ctx.get("vertical")
    if niche:
        lines.append(f"Negocio: {niche}")
    if ctx.get("business_what"):
        lines.append(f"Qué hace: {str(ctx['business_what'])[:300]}")
    if ctx.get("business_diff"):
        lines.append(f"Diferenciador: {str(ctx['business_diff'])[:200]}")
    aud = _joined(ctx, ("target_audience", "audience_age_range", "audience_gender"))
    if aud:
        lines.append(f"Audiencia: {aud}")
    goals = _joined(ctx, ("primary_goal", "goal_this_month"))
    if goals:
        lines.append(f"Objetivos: {goals}")
    voice = _joined(ctx, ("tone", "emoji_usage", "hashtag_strategy"))
    if voice:
        lines.append(f"Voz de marca: {voice}")
    lines.append(_accounts_line(ctx.get("social_accounts") or []))
    if ctx.get("uploaded_context_text"):
        lines.append("Documento de referencia del cliente:\n" + str(ctx["uploaded_context_text"])[:_UPLOADED_CAP])
    block = "# CONTEXTO DEL CLIENTE (usalo · nunca inventes datos)\n" + "\n".join(lines)
    return block[:_TOTAL_CAP]
