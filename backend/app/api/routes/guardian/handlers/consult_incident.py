"""POST /guardian/consult/incident · Claude analiza el incident/evento y SUGIERE acción (4B-5) · owner-only.

NO ejecuta nada (P4 · el owner decide). Persiste el consult en agent_memory (audit + futuro learning loop).
Modelo Sonnet 4.6 vía anthropic_adapter (I1 · routing guardian_consultor). Contexto ≤~2k tokens (I6).
"""
import json
import logging
from typing import Dict, Any, Optional, Tuple

from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.guardian.models import ConsultRequest
from app.bc_cognition.domain.persona_guardian_consultor import SYSTEM_PROMPT
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_DEFAULT_Q = "Analizá este incidente · explicá qué pasa y qué acción recomendás."
_FALLBACK = {"recommended_action": "investigar", "confidence_level": "baja", "alternative": None}


def _build_context(sb, body: ConsultRequest) -> Tuple[str, Optional[str]]:
    lines, user_id = [], None
    if body.entity_type == "incident":
        inc = (sb.table("security_incidents").select("*").eq("id", body.entity_id).limit(1).execute().data or [None])[0]
        if inc:
            user_id = inc.get("user_id")
            lines.append(f"INCIDENTE {inc['incident_type']} · severity={inc['severity']} · status={inc['status']} · {inc.get('summary') or ''}")
            lines.append(f"evidence: {json.dumps(inc.get('evidence') or {})[:300]}")
    elif body.entity_type == "user":
        user_id = body.entity_id
        lines.append(f"USUARIO {user_id}")
    elif body.entity_type == "watchlist":
        evs = (sb.table("user_security_log").select("user_id, event_type, country")
               .eq("ip_address", body.entity_id).order("created_at", desc=True).limit(5).execute().data) or []
        lines.append(f"IP EN WATCHLIST {body.entity_id} · {len(evs)} eventos asociados")
        user_id = next((e.get("user_id") for e in evs if e.get("user_id")), None)
    if user_id:
        hist = (sb.table("user_security_log").select("event_type, ip_address, country, risk_score, created_at")
                .eq("user_id", user_id).order("created_at", desc=True).limit(10).execute().data) or []
        lines.append("HISTORIAL (ultimos 10):")
        lines += [f"  {h['created_at'][:16]} {h['event_type']} ip={h.get('ip_address')} r{h.get('risk_score')}" for h in hist]
    return "\n".join(lines)[:6000], user_id


async def handle_consult_incident(body: ConsultRequest, authorization: Optional[str]) -> Dict[str, Any]:
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    context, user_id = _build_context(sb, body)
    if not context:
        return {"analysis": "Entidad no encontrada o sin contexto.", "reasoning": "Sin datos.", **_FALLBACK}
    question = body.owner_question or _DEFAULT_Q
    resp, err = await generate("guardian_consultor", system=SYSTEM_PROMPT,
                               messages=[{"role": "user", "content": f"{question}\n\nCONTEXTO:\n{context}"}],
                               max_tokens=700, temperature=0.3)
    if err is not None or resp is None:
        return {"analysis": "Consultor no disponible.", "reasoning": f"error: {err.code if err else 'none'}", **_FALLBACK}
    raw = resp.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(raw)
    except Exception:  # noqa: BLE001 — respuesta no-JSON · degradar honesto
        parsed = {"analysis": resp.text[:500], "reasoning": "respuesta no estructurada", **_FALLBACK}
    try:
        sb.table("agent_memory").insert({
            "user_id": user_id, "agent_code": "guardian_consultor", "memory_type": "episodic",
            "context": f"{body.entity_type}:{body.entity_id} · {question}"[:500],
            "decision": str(parsed.get("recommended_action"))[:200],
            "reasoning": str(parsed.get("reasoning"))[:500], "was_correct": None,
        }).execute()
    except Exception as e:  # noqa: BLE001 — audit best-effort
        logger.warning(f"consult agent_memory insert skip: {e}")
    return parsed
