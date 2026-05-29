"""Fase 1 · PASO 2 · loop agéntico de ARIA + primera tool real (split de use_aria_message · C4).

prepare_supervised_draft: ARIA prepara un borrador y lo deja en la cola Supervisado (DEBT-097) PARA
APROBACIÓN. NO publica, NO agenda a scheduled_posts · la fecha es sugerencia en metadata.

Anti-G5: el client_id es SIEMPRE el derivado server-side (arg posicional) · el schema NO lo acepta de
Claude. Gates: should_enqueue (P3 confidence≥7 · P2 agente prohibido) antes de crear.
"""
from typing import Any, Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.application import supervisado_mode_service as sup
from app.api.routes.content_lab_v3 import _content_lab_repository as cl_repo

_AGENT_CODE = "content_creator"  # P2: nunca crisis · no en ACCIONES_PROHIBIDAS
_DRAFT_CONFIDENCE = 8            # ≥ MIN_CONFIDENCE_TO_ACT (P3) · contenido normal

SCHEDULE_DEF: dict[str, Any] = {
    "name": "prepare_supervised_draft",
    "description": (
        "Prepara un borrador y lo deja en la cola Supervisado del cliente PARA SU APROBACIÓN. "
        "NO publica ni agenda · la fecha es solo una SUGERENCIA. Tras usar esta herramienta, decile al "
        "usuario con verdad que el borrador quedó PROPUESTO / EN REVISIÓN para que lo apruebe — NUNCA "
        "que ya quedó agendado o que se publicará."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "texto": {"type": "string", "description": "El contenido del post."},
            "plataforma": {"type": "string", "description": "instagram/facebook/tiktok/linkedin · opcional."},
            "fecha_sugerida": {"type": "string", "description": "ISO · solo sugerencia · NO agenda."},
        },
        "required": ["texto"],
    },
}


async def _execute_prepare_draft(client_id: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Crea draft supervisado para el client_id de SESIÓN (nunca de tool_input · anti-G5)."""
    # P2/P3: confidence≥7 + agente no prohibido · si no pasa, NO crea
    if not sup.should_enqueue({"agent_code": _AGENT_CODE, "confidence": _DRAFT_CONFIDENCE}, True):
        return {"ok": False, "mensaje": "No se preparó el borrador (no alcanzó el umbral de convicción)."}
    texto = str(tool_input.get("texto") or "").strip()
    if not texto:
        return {"ok": False, "mensaje": "No se preparó el borrador (faltó el texto del contenido)."}
    meta = sup.mark_supervisado({
        "platform": tool_input.get("plataforma") or "general",
        "fecha_sugerida": tool_input.get("fecha_sugerida"),  # SUGERENCIA · no agenda
        "origen": "aria_tool",
    })
    content_id = await cl_repo.safe_insert(
        "aria_supervised_draft", cl_repo.insert_generated_content, client_id, {
            "agent_code": _AGENT_CODE, "content_type": "text", "generated_text": texto,
            "metadata": meta, "confidence": _DRAFT_CONFIDENCE,
            "status": "draft", "compliance_passed": True,
        },
    )
    if not content_id:
        return {"ok": False, "mensaje": "No se pudo guardar el borrador. Intentá de nuevo."}
    fecha = tool_input.get("fecha_sugerida")
    cuando = f" con fecha SUGERIDA {fecha}" if fecha else ""
    return {"ok": True, "content_id": content_id, "mensaje": (
        f"Borrador preparado y dejado en la cola Supervisado del cliente{cuando}. "
        "Estado: PENDIENTE DE APROBACIÓN. NO está agendado ni se publicará hasta que el cliente "
        "lo apruebe en su panel Supervisado."
    )}


async def run_tool_loop(agent_code: str, system: str, messages: list[dict[str, Any]],
                        client_id: Optional[str]) -> tuple[Optional[str], Optional[object]]:
    """1 iteración de tool. Sin tool_use → texto normal (idéntico a hoy). Devuelve (text, err)."""
    resp, err = await generate(agent_code=agent_code, system=system, messages=messages,
                               max_tokens=1024, tools=[SCHEDULE_DEF])
    if err or resp is None:
        return None, err
    if not resp.tool_calls or not client_id:
        return resp.text, None  # conversación normal · cero cambio vs hoy

    tool_results = []
    for block in resp.tool_calls:
        out = await _execute_prepare_draft(client_id, getattr(block, "input", {}) or {})
        tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                             "content": str(out.get("mensaje") or out)})
    followup = messages + [
        {"role": "assistant", "content": resp.tool_calls},
        {"role": "user", "content": tool_results},
    ]
    # Addendum anti-hype · narra el resultado con VERDAD (P1) · solo esta llamada · NO toca persona
    narration = (system + "\n\n" + _NARRATION_RULE)
    resp2, err2 = await generate(agent_code=agent_code, system=narration, messages=followup, max_tokens=1024)
    if err2 or resp2 is None:
        return None, err2
    return resp2.text, None


_NARRATION_RULE = (
    "Acabás de preparar un borrador. Contale al usuario con VERDAD: quedó en su cola Supervisado para que "
    "lo APRUEBE. Si había fecha, es SUGERIDA. NUNCA digas que se programó, que sale automáticamente, que se "
    "publica solo ni 'sale volando' — requiere su aprobación manual en el panel Supervisado."
)
