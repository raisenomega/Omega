"""A2.1 · Marca para prompts de imagen · utilidad reusable (D2).

Fuente ÚNICA de la lógica de marca: la usan TANTO el handler n=1 (A6) COMO el puente del carrusel
(A2.4), para que el carrusel NO pierda ni duplique los colores. Mismo BC (content_lab_v3) · NO bc_cognition.
Hex limpio en DB (#rrggbb · picker + regex zod) → se concatena directo, sin normalizar. Fuentes/logo fuera.
"""
import asyncio

from app.api.routes.content_lab_v3 import _content_lab_repository as repo


def _brand_block(palette: dict) -> str:
    """Instrucción visual instructiva (NO descriptiva como el bloque de ARIA del chat) con SOLO los colores
    que existen. Sin primary → "" (cliente sin paleta · prompt idéntico a hoy · retrocompat). Movido de A6."""
    primary = palette.get("primary_color")
    if not primary:
        return ""
    parts = [f"use {primary} as primary"]
    if palette.get("secondary_color"):
        parts.append(f"{palette['secondary_color']} as secondary")
    if palette.get("accent_color"):
        parts.append(f"{palette['accent_color']} as accent color")
    return ", brand color palette: " + ", ".join(parts)


async def fetch_brand_block(client_id: str) -> str:
    """Lee la paleta del cliente (to_thread · patrón del logo) y arma el bloque (o "" si no hay). Un bloque
    por cliente · es el MISMO para las N placas de un carrusel (A2 lo concatena a cada prompt de placa)."""
    palette = await asyncio.to_thread(repo.find_client_brand_palette, client_id)
    return _brand_block(palette)
