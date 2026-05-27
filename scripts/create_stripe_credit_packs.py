#!/usr/bin/env python3
"""Crea 4 Stripe Products + Prices recurring monthly para Credit Packs (DEBT-052 FASE 4).

Uso (desde la raíz del repo):
    python scripts/create_stripe_credit_packs.py

Idempotente vía metadata `omega_credit_pack_code` · si el product ya existe,
reusa el price activo en vez de crear duplicados.

Requisitos:
    - STRIPE_SECRET_KEY como variable de entorno (export o set previo a ejecutar)
    - pip install stripe (ya en backend/requirements.txt)

Output:
    Imprime los 4 price_ids para copiar a Railway env vars (consumidos por
    bc_billing.domain.credit_pack_pricing.get_price_id_for_credit_pack):
        STRIPE_PRICE_CREDIT_PACK_MICRO=price_xxx
        STRIPE_PRICE_CREDIT_PACK_STARTER=price_xxx
        STRIPE_PRICE_CREDIT_PACK_PLUS=price_xxx
        STRIPE_PRICE_CREDIT_PACK_ULTRA=price_xxx

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

# Budgets alineados con bc_billing.domain.credit_costs.PACK_BUDGETS_USD.
PACKS = [
    {
        "code": "micro",
        "name": "Credit Pack Micro",
        "description": "Budget mensual prepagado de API ($9) · más generaciones de texto e imagen",
        "amount_usd": 9,
        "env_var": "STRIPE_PRICE_CREDIT_PACK_MICRO",
    },
    {
        "code": "starter",
        "name": "Credit Pack Starter",
        "description": "Budget mensual prepagado de API ($25) · más generaciones de texto e imagen",
        "amount_usd": 25,
        "env_var": "STRIPE_PRICE_CREDIT_PACK_STARTER",
    },
    {
        "code": "plus",
        "name": "Credit Pack Plus",
        "description": "Budget mensual prepagado de API ($59) · más generaciones de texto e imagen",
        "amount_usd": 59,
        "env_var": "STRIPE_PRICE_CREDIT_PACK_PLUS",
    },
    {
        "code": "ultra",
        "name": "Credit Pack Ultra",
        "description": "Budget mensual prepagado de API ($119) · más generaciones de texto e imagen",
        "amount_usd": 119,
        "env_var": "STRIPE_PRICE_CREDIT_PACK_ULTRA",
    },
]


def find_existing_product(code: str) -> dict | None:
    """Lookup product por metadata.omega_credit_pack_code · retorna dict o None.
    StripeObject SDK no es dict puro · acceso defensivo con try/except."""
    products = stripe.Product.list(limit=100, active=True)
    for p in products.auto_paging_iter():
        try:
            md_val = p["metadata"]["omega_credit_pack_code"]
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


def upsert_pack(pack: dict) -> str:
    existing = find_existing_product(pack["code"])
    if existing:
        price_id = find_active_price(existing.id)
        if price_id:
            print(f"  [reuse] {pack['name']} · product {existing.id} · price {price_id}", file=sys.stderr)
            return price_id
        product = existing
    else:
        product = stripe.Product.create(
            name=pack["name"],
            description=pack["description"],
            metadata={"omega_credit_pack_code": pack["code"]},
        )
        print(f"  [created product] {product.id}", file=sys.stderr)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=pack["amount_usd"] * 100,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"omega_credit_pack_code": pack["code"]},
    )
    print(f"  [created price]   {price.id}", file=sys.stderr)
    return price.id


def main() -> None:
    print("Creating/syncing 4 Credit Pack products in Stripe...\n", file=sys.stderr)
    lines = []
    for pack in PACKS:
        print(f"→ {pack['name']} (${pack['amount_usd']}/mes)", file=sys.stderr)
        price_id = upsert_pack(pack)
        lines.append(f"{pack['env_var']}={price_id}")
        print(file=sys.stderr)
    print("\nCopy these to Railway env vars (no commitear este output):\n", file=sys.stderr)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
