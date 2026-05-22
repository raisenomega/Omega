"""Use case · build BrandDNA para un cliente.

Orquesta: repo Supabase → builder puro → BrandDNA. Síncrono (Supabase
es síncrono). Llamado desde api/routes/content_lab_v3 antes de generate().

DEBT-044 (Sprint 2): persistir DNA computado + cron refresh diario para
reducir compute por request + maximizar cache hit rate Anthropic.
"""
from app.bc_cognition.application._brand_dna_builder import build_brand_dna
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.infrastructure.brand_voice_corpus_repository import (
    fetch_recent_corpus,
)


def build_dna_for_client(client_id: str, limit: int = 20) -> BrandDNA:
    corpus = fetch_recent_corpus(client_id, limit=limit)
    return build_brand_dna(corpus)
