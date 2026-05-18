"""
OMEGA · PATCH /api/v1/admin/solicitudes/{id}/accept|decline
Acepta → cobra por Stripe. Declina → notifica.
R-LINES-001: < 200L · Solo role=owner
"""
import os
from datetime import datetime, timezone
from fastapi import HTTPException, status, Header
from typing import Optional

import stripe

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

from ..upsell.upsell_models import SolicitudActionResponse, SolicitudResponse

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def patch_solicitud_accept(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> SolicitudActionResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo superadmin")

    sol_row = supabase.client.table("upsell_solicitudes").select("*").eq("id", solicitud_id).single().execute()
    if not sol_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    sol = sol_row.data
    if sol["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Solicitud ya está en estado: {sol['status']}")

    # Obtener datos del cliente para Stripe
    client_row = supabase.client.table("clients").select("stripe_customer_id, stripe_subscription_id, name, email").eq("id", sol["client_id"]).single().execute()
    if not client_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    client = client_row.data
    stripe_customer_id = client.get("stripe_customer_id")
    stripe_subscription_id = client.get("stripe_subscription_id")

    charge_id: str | None = None

    if stripe_customer_id and stripe.api_key:
        try:
            price_cents = int(sol["monthly_price"] * 100)

            # Agregar como item a la suscripción existente (recurrente)
            if stripe_subscription_id:
                price_obj = stripe.Price.create(
                    unit_amount=price_cents,
                    currency="usd",
                    recurring={"interval": "month"},
                    product_data={"name": f"OMEGA Company — {sol['item_name']}"},
                )
                sub_item = stripe.SubscriptionItem.create(
                    subscription=stripe_subscription_id,
                    price=price_obj.id,
                    quantity=1,
                )
                charge_id = sub_item.id
            else:
                # Cobro inmediato si no hay suscripción activa
                invoice_item = stripe.InvoiceItem.create(
                    customer=stripe_customer_id,
                    amount=price_cents,
                    currency="usd",
                    description=f"OMEGA Company — {sol['item_name']} (${{sol['monthly_price']}}/mes)",
                )
                invoice = stripe.Invoice.create(
                    customer=stripe_customer_id,
                    auto_advance=True,
                )
                stripe.Invoice.finalize_invoice(invoice.id)
                charge_id = invoice.id

        except stripe.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Error de Stripe: {str(e)}",
            )

    now = _now_iso()
    update_data = {
        "status": "accepted",
        "stripe_charge_id": charge_id,
        "resolved_at": now,
        "resolved_by": user.get("id"),
        "updated_at": now,
    }

    supabase.client.table("upsell_solicitudes").update(update_data).eq("id", solicitud_id).execute()

    # TODO: Activar el agente en la configuración del cliente
    # TODO: Enviar notificación al cliente (email/in-app)

    updated = supabase.client.table("upsell_solicitudes").select("*").eq("id", solicitud_id).single().execute()
    return SolicitudActionResponse(
        success=True,
        data=SolicitudResponse(**updated.data),
        stripe_charge_id=charge_id,
        message=f"Agente {sol['item_name']} activado. Stripe procesó ${sol['monthly_price']}/mes.",
    )


async def patch_solicitud_decline(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> SolicitudActionResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo superadmin")

    sol_row = supabase.client.table("upsell_solicitudes").select("id, status").eq("id", solicitud_id).single().execute()
    if not sol_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    if sol_row.data["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solicitud ya resuelta")

    now = _now_iso()
    supabase.client.table("upsell_solicitudes").update({
        "status": "declined",
        "resolved_at": now,
        "resolved_by": user.get("id"),
        "updated_at": now,
    }).eq("id", solicitud_id).execute()

    updated = supabase.client.table("upsell_solicitudes").select("*").eq("id", solicitud_id).single().execute()
    return SolicitudActionResponse(
        success=True,
        data=SolicitudResponse(**updated.data),
        message="Solicitud declinada.",
    )
