#!/usr/bin/env python3
"""Crea el Stripe Product + Price recurring monthly del plan ENTERPRISE ($199/mes).

Uso (desde la raíz del repo):
    python scripts/create_stripe_enterprise.py

Idempotente vía metadata `omega_plan_code` · si el product ya existe, reusa el
price activo en vez de crear duplicados. (basic/pro se crean aparte · esta script
cubre solo enterprise · DEBT-076 self-serve checkout.)

Requisitos:
    - STRIPE_SECRET_KEY como variable de entorno (export o set previo a ejecutar)
    - pip install stripe (ya en backend/requirements.txt)

Output:
    Imprime el price_id para copiar a Railway env vars (consumido por
    bc_billing.domain.plan_pricing.get_price_id_for_plan):
        STRIPE_PRICE_ENTERPRISE=price_xxx

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

# Precio canónico MODELO_NEGOCIO §3 (ENTERPRISE $199/mes · ARIA Nivel 4 incluido).
PLANS = [
    {
        "code": "enterprise",
        "name": "OmegaRaisen Enterprise",
        "description": "192 posts/mes · 12 cuentas · todas las features · ARIA Nivel 4 · soporte prioritario",
        "amount_usd": 199,
        "env_var": "STRIPE_PRICE_ENTERPRISE",
    },
]


def find_existing_product(code: str) -> dict | None:
    """Lookup product por metadata.omega_plan_code · retorna dict o None.
    StripeObject SDK no es dict puro · acceso defensivo con try/except."""
    products = stripe.Product.list(limit=100, active=True)
    for p in products.auto_paging_iter():
        try:
            md_val = p["metadata"]["omega_plan_code"]
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


def upsert_plan(plan: dict) -> str:
    existing = find_existing_product(plan["code"])
    if existing:
        price_id = find_active_price(existing.id)
        if price_id:
            print(f"  [reuse] {plan['name']} · product {existing.id} · price {price_id}", file=sys.stderr)
            return price_id
        product = existing
    else:
        product = stripe.Product.create(
            name=plan["name"],
            description=plan["description"],
            metadata={"omega_plan_code": plan["code"]},
        )
        print(f"  [created product] {product.id}", file=sys.stderr)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=plan["amount_usd"] * 100,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"omega_plan_code": plan["code"]},
    )
    print(f"  [created price]   {price.id}", file=sys.stderr)
    return price.id


def main() -> None:
    print("Creating/syncing ENTERPRISE plan product in Stripe...\n", file=sys.stderr)
    lines = []
    for plan in PLANS:
        print(f"→ {plan['name']} (${plan['amount_usd']}/mes)", file=sys.stderr)
        price_id = upsert_plan(plan)
        lines.append(f"{plan['env_var']}={price_id}")
        print(file=sys.stderr)
    print("\nCopy these to Railway env vars (no commitear este output):\n", file=sys.stderr)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
