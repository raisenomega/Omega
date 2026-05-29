"""Fase 1 · PASO 2 · loop agéntico de ARIA + tool prepare_supervised_draft.

La creación del borrador vive en `_aria_draft.execute_prepare_draft` (split · C4 · valida fecha
→ B2). Aquí quedan el schema de la tool, el loop de 1 iteración y la regla anti-hype (P1).
Anti-G5: el client_id es SIEMPRE el derivado server-side · el schema NO lo acepta de Claude.
"""
from typing import Any, Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.application._aria_draft import execute_prepare_draft

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


async def run_tool_loop(agent_code: str, system: str, messages: list[dict[str, Any]],
                        client_id: Optional[str], timezone: Optional[str] = None,
                        ) -> tuple[Optional[str], Optional[object]]:
    """1 iteración de tool. Sin tool_use → texto normal (idéntico a hoy). Devuelve (text, err)."""
    system = f"{system}\n\n{_RESPONSE_RULES}"  # reglas de respuesta · cierre del system (recency · P1)
    resp, err = await generate(agent_code=agent_code, system=system, messages=messages,
                               max_tokens=1024, tools=[SCHEDULE_DEF])
    if err or resp is None:
        return None, err
    if not resp.tool_calls or not client_id:
        return resp.text, None  # conversación normal · cero cambio vs hoy

    tool_results = []
    for block in resp.tool_calls:
        out = await execute_prepare_draft(client_id, getattr(block, "input", {}) or {}, timezone)
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

# Reglas de respuesta · se anexan al FINAL del system (recency) · honestidad P1: ARIA es la cara que
# dirige al catálogo, NO el catálogo. La verdad de cada sección vive en su pantalla, no acá.
_RESPONSE_RULES = (
    "REGLAS DE RESPUESTA (cumplilas SIEMPRE, por encima de todo lo anterior):\n"
    "1) Si te preguntan qué hace una sección, o te piden algo que vive en otra página, "
    "respondé en UNA línea con esta forma exacta: «Eso lo ves en {sección} — te llevo ahí.» "
    "No listes ni describas las funciones de esa sección: cada sección muestra su verdad "
    "cuando el cliente llega.\n"
    "2) Sé firme y clara con lo que VOS SÍ hacés (preparar borradores para su aprobación, "
    "dirigir al cliente dentro de OMEGA): eso lo ofrecés con seguridad, nunca lo dudes ni lo niegues."
)
