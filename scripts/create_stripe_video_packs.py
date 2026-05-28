#!/usr/bin/env python3
"""Crea 3 Stripe Products + Prices recurring monthly para Video Packs (DEBT-VID-001).

Uso (desde la raíz del repo):
    python scripts/create_stripe_video_packs.py

Idempotente vía metadata `omega_video_pack_code` · si el product ya existe,
reusa el price activo en vez de crear duplicados.

Requisitos:
    - STRIPE_SECRET_KEY como variable de entorno (export o set previo a ejecutar)
    - pip install stripe (ya en backend/requirements.txt)

Output:
    Imprime los 3 price_ids para copiar a Railway env vars:
        STRIPE_PRICE_VIDEO_PACK_STARTER=price_xxx
        STRIPE_PRICE_VIDEO_PACK_CREATOR=price_xxx
        STRIPE_PRICE_VIDEO_PACK_CINEMATIC_PRO=price_xxx

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

PACKS = [
    {
        "code": "starter",
        "name": "Video Pack Starter",
        "description": "6 videos/mes × 8s · ARIA prompt + Brand DNA auto",
        "amount_usd": 39,
        "env_var": "STRIPE_PRICE_VIDEO_PACK_STARTER",
    },
    {
        "code": "creator",
        "name": "Video Pack Creator",
        "description": "5 videos/mes × 30s · script narrativo ARIA + revisión tono",
        "amount_usd": 95,
        "env_var": "STRIPE_PRICE_VIDEO_PACK_CREATOR",
    },
    {
        "code": "cinematic_pro",
        "name": "Video Pack Cinematic Pro",
        "description": "3 videos/mes × 60s · HOOK-DESARROLLO-CTA · agente dedicado",
        "amount_usd": 125,
        "env_var": "STRIPE_PRICE_VIDEO_PACK_CINEMATIC_PRO",
    },
]


def find_existing_product(code: str) -> dict | None:
    """Lookup product por metadata.omega_video_pack_code · retorna dict o None.
    StripeObject SDK no es dict puro · acceso defensivo con try/except."""
    products = stripe.Product.list(limit=100, active=True)
    for p in products.auto_paging_iter():
        try:
            md_val = p["metadata"]["omega_video_pack_code"]
        except (KeyError, TypeError):
            md_val = None
        if md_val == code:
            return p
    return None


def find_active_price(product_id: str) -> str | None:
    """Retorna el primer price activo recurring del product · None si no hay."""
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
            metadata={"omega_video_pack_code": pack["code"]},
        )
        print(f"  [created product] {product.id}", file=sys.stderr)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=pack["amount_usd"] * 100,
        currency="usd",
        recurring={"interval": "month"},
        metadata={"omega_video_pack_code": pack["code"]},
    )
    print(f"  [created price]   {price.id}", file=sys.stderr)
    return price.id


def main() -> None:
    print("Creating/syncing 3 Video Pack products in Stripe...\n", file=sys.stderr)
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
