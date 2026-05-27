"""DEBT-052 F4 · dispatch de checkout.session.completed para addons/packs.

Extraído de _webhook_handlers.on_checkout_completed para mantener C4 ≤100L (mismo
patrón que la extracción reseller_aria de DEBT-046). Retorna True si el evento era
un addon / video-pack / credit-pack (ya manejado acá); False si es un plan upgrade
(lo procesa on_checkout_completed). Lógica de addon/video idéntica a la original.
"""
import logging
from typing import Optional
from app.bc_billing.application._addon_handlers import (
    handle_addon_activation, handle_video_pack_activation,
)
from app.bc_billing.application.reseller_aria import handle_reseller_addon_activation
from app.bc_billing.application._credit_pack_handlers import handle_credit_pack_enrollment
from app.bc_billing.application._agent_addon_handlers import handle_agent_addon_activation
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


async def dispatch_addon_or_pack(
    metadata: dict, sub_id: Optional[str], supabase: SupabaseService,
) -> bool:
    """Maneja addon/video-pack/credit-pack según metadata. True si manejó el evento."""
    client_id = metadata.get("client_id")
    addon_code = metadata.get("addon_code")
    if addon_code:
        if addon_code == "aria_premium_reseller":
            reseller_id = metadata.get("reseller_id")
            if not all([reseller_id, sub_id]):
                logger.warning("reseller addon checkout.completed con data faltante")
                return True
            await handle_reseller_addon_activation(reseller_id, addon_code, sub_id, supabase)
            return True
        if not all([client_id, sub_id]):
            logger.warning("addon checkout.completed con data faltante")
            return True
        await handle_addon_activation(client_id, addon_code, sub_id, supabase)
        return True
    video_pack_code = metadata.get("video_pack_code")
    if video_pack_code:
        if not all([client_id, sub_id]):
            logger.warning("video_pack checkout.completed con data faltante")
            return True
        await handle_video_pack_activation(client_id, video_pack_code, sub_id, supabase)
        return True
    credit_pack_code = metadata.get("credit_pack_code")
    if credit_pack_code:
        if not all([client_id, sub_id]):
            logger.warning("credit_pack checkout.completed con data faltante")
            return True
        await handle_credit_pack_enrollment(client_id, credit_pack_code, sub_id, supabase)
        return True
    agent_addon_code = metadata.get("agent_addon_code")
    if agent_addon_code:
        if not all([client_id, sub_id]):
            logger.warning("agent_addon checkout.completed con data faltante")
            return True
        await handle_agent_addon_activation(client_id, agent_addon_code, sub_id, supabase)
        return True
    return False
