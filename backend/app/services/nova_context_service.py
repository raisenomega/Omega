"""
Nova Context Service — Builds NOVA system prompts dynamically per client.
DDD: Application layer. Business logic only — zero direct Supabase access.
Filosofía: No velocity, only precision 🐢💎
"""
import logging

from app.domain.nova_entities import (
    NovaFullContext,
    NovaContextResponse,
    UpdateContextRequest,
)
from app.infrastructure.repositories.nova_repository import NovaRepository
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

# ─── Tier capability blocks ────────────────────────────────────────────────────

_TIER_RULES: dict[str, str] = {
    "sistema_only": (
        "CAPACIDADES ACTIVAS (Plan Sistema):\n"
        "- Modo: Reactiva — respondo cuando el cliente escribe\n"
        "- Límite mensual: 100 mensajes | 30 contenidos | máx. 2 redes sociales\n"
        "- Monitoreo de competidores: no disponible en este tier\n"
        "- Acceso a directores nombrados: no disponible en este tier"
    ),
    "nova_dedicated": (
        "CAPACIDADES ACTIVAS (Plan Nova Dedicated):\n"
        "- Modo: Proactiva — puedo iniciar conversaciones y sugerir acciones\n"
        "- Sin límite de mensajes ni de contenidos generados\n"
        "- Monitoreo activo de hasta 3 competidores\n"
        "- Acceso completo a métricas de todas las redes conectadas"
    ),
    "company": (
        "CAPACIDADES ACTIVAS (Plan Company):\n"
        "- Modo: Proactiva + Estratégica — iniciativa completa\n"
        "- Sin límite de mensajes ni de contenidos generados\n"
        "- Monitoreo de competidores ilimitado\n"
        "- Acceso directo a tu equipo de directores con identidad propia"
    ),
}


class NovaContextService:
    """
    Service for NOVA context operations.
    NEVER touches Supabase directly — all access via NovaRepository.
    """

    def __init__(self, supabase: SupabaseService) -> None:
        self._repo = NovaRepository(supabase)  # [R-DDD-001]

    async def get_context(self, client_id: str) -> NovaContextResponse:
        """Fetch nova_full_context and build dynamic system prompt."""
        context = self._repo.get_full_context(client_id)
        if context is None:
            raise ValueError(f"No context found for client_id: {client_id}")
        return self._build_response(context)

    async def update_context(
        self, client_id: str, request: UpdateContextRequest
    ) -> NovaContextResponse:
        """Write non-None fields to client_context, return refreshed context."""
        update_data: dict[str, str] = {
            k: v
            for k, v in request.model_dump().items()
            if v is not None
        }
        if update_data:
            self._repo.update_context_fields(client_id, update_data)
        return await self.get_context(client_id)

    async def append_learning(
        self, client_id: str, key: str, value: str
    ) -> dict[str, str]:
        """Append a NOVA learning entry and confirm."""
        self._repo.append_learning(client_id, key, value)
        logger.info(f"Learning appended for client {client_id}: {key}")
        return {"status": "ok", "client_id": client_id, "key": key}

    # ─── Private ──────────────────────────────────────────────────────────────

    def _build_response(self, ctx: NovaFullContext) -> NovaContextResponse:
        return NovaContextResponse(
            client_id=ctx.client_id,
            client_name=ctx.client_name,
            nova_tier=ctx.nova_tier,
            system_prompt=self._build_prompt(ctx),
            context_raw=ctx,
        )

    def _build_prompt(self, ctx: NovaFullContext) -> str:
        """
        Construct dynamic system prompt from client context.
        Rule: None/empty fields are omitted — 'None' NEVER appears in the text.
        """
        lines: list[str] = [
            f"Eres NOVA, la CEO de OMEGA y asistente estratégica de {ctx.client_name}.\n"
        ]

        # — Client profile ——————————————————————————————————————————————————
        profile: list[str] = []
        if ctx.niche:
            profile.append(f"- Industria: {ctx.niche}"
                           + (f" | Geo: {ctx.business_geo}" if ctx.business_geo else "")
                           + (f" | Tono: {ctx.tone}" if ctx.tone else ""))
        if ctx.business_what:
            profile.append(f"- Qué venden: {ctx.business_what}")
        if ctx.business_to_whom:
            profile.append(f"- A quién: {ctx.business_to_whom}")
        if ctx.business_diff:
            profile.append(f"- Diferenciador: {ctx.business_diff}")
        if ctx.goal_this_month:
            profile.append(f"- Objetivo este mes: {ctx.goal_this_month}")
        if ctx.goal_priority_now:
            profile.append(f"- Prioridad ahora: {ctx.goal_priority_now}")
        if profile:
            lines += ["SOBRE TU CLIENTE:"] + profile + [""]

        # — History ————————————————————————————————————————————————————————
        history: list[str] = []
        if ctx.what_worked:
            history.append(f"- Qué ha funcionado: {ctx.what_worked}")
        if ctx.what_failed:
            history.append(f"- Qué no ha funcionado: {ctx.what_failed}")
        if history:
            lines += ["HISTORIAL:"] + history + [""]

        # — Learnings ——————————————————————————————————————————————————————
        if ctx.nova_learnings:
            lines.append("APRENDIZAJES PREVIOS:")
            for entry in ctx.nova_learnings:
                for k, v in entry.items():
                    lines.append(f"- {k}: {v}")
            lines.append("")

        # — Tier capabilities ——————————————————————————————————————————————
        tier_key = ctx.nova_tier if ctx.nova_tier in _TIER_RULES else "sistema_only"
        lines.append(_TIER_RULES[tier_key])

        # Company tier: list available directors
        if tier_key == "company" and ctx.company_agents:
            lines += ["", "TU EQUIPO DE DIRECTORES:"]
            for agent in ctx.company_agents:
                lines.append(f"  • {agent}")
            lines.append("")

        # — Publishing networks ————————————————————————————————————————————
        if ctx.nova_can_publish:
            lines.append(f"\nREDES DONDE PUEDES PUBLICAR: {', '.join(ctx.nova_can_publish)}")

        # — Custom instructions (highest priority — always last) ———————————
        if ctx.custom_instructions:
            lines.append(f"\nINSTRUCCIONES ESPECIALES:\n{ctx.custom_instructions}")

        return "\n".join(lines)
