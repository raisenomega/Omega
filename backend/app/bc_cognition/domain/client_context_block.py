"""Bloque de contexto del cliente para ARIA (dominio puro · A2).

Incluye: perfil completado (X/10 + ✅/❌ por sección · ARIA guía qué falta) +
contexto real (negocio, audiencia, objetivos, voz, cuentas, doc). Cap total 2000 (I6).
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


def _sections(ctx: dict[str, Any]) -> list[tuple[bool, str, str]]:
    """(lleno, etiqueta, detalle) por las 10 secciones · espejo EXACTO de sectionsFilled
    (frontend) y calc_completion_percent (backend) · los 3 calculadores convergen."""
    cl = ctx.get("_client") or {}
    ba = ctx.get("_brand_assets") or {}
    bv = ctx.get("brand_voice") or {}
    acc = ctx.get("social_accounts") or []
    return [
        (bool(cl.get("name") and cl.get("industry") and cl.get("region")), "Identidad", str(cl.get("name") or "")),
        (any(ctx.get(k) for k in ("niche", "business_what", "business_to_whom", "business_diff")), "Negocio", str(ctx.get("niche") or ctx.get("vertical") or "")),
        (any(ctx.get(k) for k in ("target_audience", "audience_age_range", "competitors")), "Audiencia", str(ctx.get("target_audience") or "")),
        (bool(ctx.get("tone")) or bool(bv.get("keywords")) or bool(ctx.get("preferred_formats")), "Voz de marca", str(ctx.get("tone") or "")),
        (any(ctx.get(k) for k in ("primary_goal", "goal_this_month", "success_metric")), "Objetivos", str(ctx.get("primary_goal") or ctx.get("goal_this_month") or "")),
        (any(ctx.get(k) for k in ("has_existing_content", "best_post_url", "what_worked")), "Historial de contenido", ""),
        (len(acc) > 0, "Cuentas sociales", ", ".join(str(a.get("platform")) for a in acc if a.get("platform"))),
        (any(ctx.get(k) for k in ("custom_instructions", "emergency_contact_name", "preferred_publishing_hours")), "Instrucciones especiales", ""),
        (bool(ba.get("primary_color")) or bool(ba.get("logo_file_id")), "Identidad visual", ""),
        (int(ctx.get("_samples_count") or 0) > 0, "Ejemplos de contenido", ""),
    ]


def _completion_lines(ctx: dict[str, Any]) -> list[str]:
    s = _sections(ctx)
    out = [f"Perfil completado: {sum(1 for f, _, _ in s if f)}/10 secciones."]
    for filled, label, detail in s:
        if filled:
            out.append(f"✅ {label}: {detail[:50]}" if detail else f"✅ {label}")
        else:
            out.append(f"❌ {label}: sin datos")
    return out


def build_client_context_block(ctx: dict[str, Any]) -> str:
    """Perfil (X/10 + qué falta) + contexto real · total ≤2000 chars (uploaded capado)."""
    lines = _completion_lines(ctx)
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
