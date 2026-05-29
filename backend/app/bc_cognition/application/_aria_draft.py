"""Creación del borrador supervisado de ARIA (split de _aria_tools · C4).

ARIA deja un borrador en la cola Supervisado (DEBT-097) PARA APROBACIÓN. NO publica, NO agenda.
La fecha es SUGERENCIA validada server-side: si no parsea a ISO futuro válido → B2 (sin fecha ·
"agéndalo en el Calendario"). NUNCA inventa ni autocorrige (el determinismo vive en la validación).
Anti-G5: el client_id es SIEMPRE el de sesión (arg posicional), nunca de tool_input.
"""
from typing import Any, Optional

from app.bc_cognition.application import supervisado_mode_service as sup
from app.bc_cognition.application._aria_temporal_context import now_for
from app.bc_cognition.domain.aria_temporal import resolve_future_iso
from app.api.routes.content_lab_v3 import _content_lab_repository as cl_repo

_AGENT_CODE = "content_creator"  # P2: nunca crisis · no en ACCIONES_PROHIBIDAS
_DRAFT_CONFIDENCE = 8            # ≥ MIN_CONFIDENCE_TO_ACT (P3) · contenido normal


async def execute_prepare_draft(client_id: str, tool_input: dict[str, Any],
                                timezone: Optional[str] = None) -> dict[str, Any]:
    """Crea draft para el client_id de SESIÓN. Valida fecha contra el 'ahora' → B2 si no es futuro."""
    # P2/P3: confidence≥7 + agente no prohibido · si no pasa, NO crea
    if not sup.should_enqueue({"agent_code": _AGENT_CODE, "confidence": _DRAFT_CONFIDENCE}, True):
        return {"ok": False, "mensaje": "No se preparó el borrador (no alcanzó el umbral de convicción)."}
    texto = str(tool_input.get("texto") or "").strip()
    if not texto:
        return {"ok": False, "mensaje": "No se preparó el borrador (faltó el texto del contenido)."}
    fecha = resolve_future_iso(tool_input.get("fecha_sugerida"), now_for(timezone))  # None → B2
    meta = sup.mark_supervisado({
        "platform": tool_input.get("plataforma") or "general",
        "fecha_sugerida": fecha,  # validada · SUGERENCIA · no agenda
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
    cuando = (f" con fecha SUGERIDA {fecha}" if fecha
              else " sin fecha — agéndalo tú en el Calendario de tu panel Supervisado")
    return {"ok": True, "content_id": content_id, "mensaje": (
        f"Borrador preparado y dejado en la cola Supervisado del cliente{cuando}. "
        "Estado: PENDIENTE DE APROBACIÓN. NO está agendado ni se publicará hasta que el cliente "
        "lo apruebe en su panel Supervisado."
    )}
