#!/usr/bin/env python3
"""Crea 5 Stripe Products + Prices recurring monthly para Agent Add-Ons (/add-ons · Agentes IA).

Agentes vendibles (tiers de _publisher_packs_data / _creative_packs_data / _trends_pack_data):
Publicador (Rex) · Creativo (Rafa) · Tendencias (Maya).

Uso (desde la raíz del repo):
    python scripts/create_stripe_agent_addons.py

Idempotente vía metadata `omega_agent_addon_code` · si el product ya existe, reusa
el price activo en vez de crear duplicados.

NOTA DE ALCANCE (honesto): este script SOLO provisiona los productos en Stripe. El
wiring de backend (campos settings.stripe_price_agent_*, get_price_id_for_agent_addon,
endpoint de checkout) NO existe todavía → la página /add-ons hoy muestra "Próximamente".
Conectar el checkout (patrón useVideoPackCheckout) es una fase futura. Crear los
productos ahora deja la catálogo de Stripe listo · NO cobra a nadie.

Requisitos:
    - STRIPE_SECRET_KEY como variable de entorno (export o set previo a ejecutar)
    - pip install stripe (ya en backend/requirements.txt)

Output (env vars sugeridas · aún sin consumidor backend · ver NOTA DE ALCANCE):
        STRIPE_PRICE_AGENT_PUBLISHER_ESENCIAL=price_xxx
        STRIPE_PRICE_AGENT_PUBLISHER_PRO=price_xxx
        STRIPE_PRICE_AGENT_CREATIVE_ESENCIAL=price_xxx
        STRIPE_PRICE_AGENT_CREATIVE_PRO=price_xxx
        STRIPE_PRICE_AGENT_TRENDS_UNICO=price_xxx

NO commitear el output del script (los price_ids son IDs externos · viven
en Railway env vars · NO en archivos del repo).
"""
from __future__ import annotations

import os
import sys

import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
if not STRIPE_SECRET_KEY:
    print("ERROR: STRIPE_SECRET_KEY no está en el entorno. Setealá antes de ejecutar.", file=sys.stderr)
    sys.exit(1)
stripe.api_key = STRIPE_SECRET_KEY

# Precios alineados con src/components/addons/_*_packs_data.ts (single source frontend).
ADDONS = [
    {
        "code": "publisher_esencial",
        "name": "Agente Publicador Esencial",
        "description": "Planifica y programa hasta 7 posts/semana con ARIA · Brand Voice · alertas",
        "amount_usd": 19,
        "env_var": "STRIPE_PRICE_AGENT_PUBLISHER_ESENCIAL",
    },
    {
        "code": "publisher_pro",
        "name": "Agente Publicador Pro",
        "description": "Todo Esencial + plan semanal automático · mejor día/hora · reporte semanal",
        "amount_usd": 29,
        "env_var": "STRIPE_PRICE_AGENT_PUBLISHER_PRO",
    },
    {
        "code": "creative_esencial",
        "name": "Agente Creativo Esencial",
        "description": "Captions IG/TikTok/LinkedIn + imágenes con Brand Voice · 30 formatos · A/B",
        "amount_usd": 25,
        "env_var": "STRIPE_PRICE_AGENT_CREATIVE_ESENCIAL",
    },
    {
        "code": "creative_pro",
        "name": "Agente Creativo Pro",
        "description": "Todo Esencial + videos Veo 3.1 · ARIA revisa prompt · Brand DNA completo",
        "amount_usd": 35,
        "env_var": "STRIPE_PRICE_AGENT_CREATIVE_PRO",
    },
    {
        "code": "trends_unico",
        "name": "Agente de Tendencias",
        "description": "Tendencias en tiempo real · monitoreo de competencia · contexto para ARIA",
        "amount_usd": 15,
        "env_var": "STRIPE_PRICE_AGENT_TRENDS_UNICO",
    },
]


def find_existing_product(code: str) -> dict | None:
    """Lookup product por metadata.omega_agent_addon_code · retorna dict o None.
    StripeObject SDK no es dict puro · acceso defensivo con try/except."""
    products = stripe.Product.list(limit=100, active=True)
    for p in products.auto_paging_iter():
        try:
            md_val = p["metadata"]["omega_agent_addon_code"]
        except (KeyError, TypeError):
            md_val = None
        if md_val == code:
            return p
    return None


def find_active_price(product_id: str) -> str | None:
    """Retorna el primer price activo recurring mensual del product · None si no hay."""
    prices = stripe.Price.list(product=product_id, active=True, limit=10)
    for pr in prices.data:
        if pr.recurring and pr.recurring.interval == "month":
            return pr.id
    return None


def upsert_addon(addon: dict) -> str:
    existing = find_existing_product(addon["code"])
    if existing:
        price_id = find_active_price(existing.id)
        if price_id:
            print(f"  [reuse] {addon['name']} · product {existing.id} · price {price_id}", file=sys.stderr)
            return price_id
        product = existing
    else:
        product = stripe.Product.create(
            name=addon["name"],
            description=addon["description"],
            metadata={"omega_agent_addon_code": addon["code"]},
        )
        print(f"  [created product] {product.id}", file=sys.stderr)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=addon["amount_usd"] * 100,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"omega_agent_addon_code": addon["code"]},
    )
    print(f"  [created price]   {price.id}", file=sys.stderr)
    return price.id


def main() -> None:
    print("Creating/syncing 5 Agent Add-On products in Stripe...\n", file=sys.stderr)
    lines = []
    for addon in ADDONS:
        print(f"→ {addon['name']} (${addon['amount_usd']}/mes)", file=sys.stderr)
        price_id = upsert_addon(addon)
        lines.append(f"{addon['env_var']}={price_id}")
        print(file=sys.stderr)
    print("\nCopy these to Railway env vars (no commitear este output):\n", file=sys.stderr)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
