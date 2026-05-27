#!/usr/bin/env python3
"""Crea 2 Stripe Products + Prices recurring monthly para ARIA Premium (DEBT-037 / DEBT-046).

Uso (desde la raíz del repo):
    python scripts/create_stripe_aria_premium.py

Idempotente vía metadata `omega_addon_code` · si el product ya existe, reusa el
price activo en vez de crear duplicados.

Requisitos:
    - STRIPE_SECRET_KEY como variable de entorno (export o set previo a ejecutar)
    - pip install stripe (ya en backend/requirements.txt)

Output:
    Imprime los 2 price_ids para copiar a Railway env vars (consumidos por
    bc_billing.domain.plan_pricing.get_price_id_for_addon):
        STRIPE_PRICE_ARIA_PREMIUM_CLIENT=price_xxx
        STRIPE_PRICE_ARIA_PREMIUM_RESELLER=price_xxx

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

# addon_code alineado con plan_pricing.ADDON_CODES · sube aria_level +1 (max 4).
ADDONS = [
    {
        "code": "aria_premium_client",
        "name": "ARIA Premium (Cliente)",
        "description": "Sube a tu cliente un nivel ARIA (+1 · máx 4) · análisis y predicciones avanzadas",
        "amount_usd": 12,
        "env_var": "STRIPE_PRICE_ARIA_PREMIUM_CLIENT",
    },
    {
        "code": "aria_premium_reseller",
        "name": "ARIA Premium (Reseller)",
        "description": "ARIA Premium en el contexto del reseller (NOVA reseller) · +1 nivel",
        "amount_usd": 25,
        "env_var": "STRIPE_PRICE_ARIA_PREMIUM_RESELLER",
    },
]


def find_existing_product(code: str) -> dict | None:
    """Lookup product por metadata.omega_addon_code · retorna dict o None.
    StripeObject SDK no es dict puro · acceso defensivo con try/except."""
    products = stripe.Product.list(limit=100, active=True)
    for p in products.auto_paging_iter():
        try:
            md_val = p["metadata"]["omega_addon_code"]
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
            metadata={"omega_addon_code": addon["code"]},
        )
        print(f"  [created product] {product.id}", file=sys.stderr)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=addon["amount_usd"] * 100,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"omega_addon_code": addon["code"]},
    )
    print(f"  [created price]   {price.id}", file=sys.stderr)
    return price.id


def main() -> None:
    print("Creating/syncing 2 ARIA Premium addon products in Stripe...\n", file=sys.stderr)
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
