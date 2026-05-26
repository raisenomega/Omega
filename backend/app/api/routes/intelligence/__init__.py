"""Intelligence 🧠 · Centro de Inteligencia Fase 1.

Scraping puro (sin Claude · NON-NEGOTIABLE: solo Anthropic para texto/razonamiento,
este módulo no genera texto · solo extrae HTML). Endpoint web-analysis con caché
read-through 24h sobre analytics_snapshots (migración 00027).
"""
from .router import router

__all__ = ["router"]
