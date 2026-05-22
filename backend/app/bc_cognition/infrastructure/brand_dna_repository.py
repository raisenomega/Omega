"""Repository client_brand_dna · persistencia DNA + listing de clients.

DEBT-044 · trigger SQL en brand_voice_corpus setea last_computed_at=NULL
cuando hay cambio · lectura lazy recomputa si stale (ver use_brand_dna).
Pattern: función libre síncrona + singleton _sb() interno.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb():
    return get_supabase_service().client


def fetch_persisted_dna(client_id: str) -> Optional[dict[str, Any]]:
    """Lee fila persistida · retorna dict con dna_jsonb + last_computed_at o None."""
    try:
        r = (
            _sb().table("client_brand_dna")
            .select("dna_jsonb, score, last_computed_at, last_corpus_size")
            .eq("client_id", client_id).limit(1).execute()
        )
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(
            f"fetch_persisted_dna failed · client={client_id}: {e}", exc_info=True,
        )
        return None


def upsert_persisted_dna(client_id: str, dna_dict: dict, corpus_size: int) -> None:
    """UPSERT por client_id (PK) · setea last_computed_at = now() en cada llamada."""
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        _sb().table("client_brand_dna").upsert({
            "client_id": client_id,
            "dna_jsonb": dna_dict,
            "score": float(dna_dict.get("score", 0.0)),
            "last_computed_at": now_iso,
            "last_corpus_size": corpus_size,
            "updated_at": now_iso,
        }).execute()
    except Exception as e:
        logger.error(
            f"upsert_persisted_dna failed · client={client_id}: {e}", exc_info=True,
        )


def fetch_active_client_ids() -> list[str]:
    """Lista client_ids para cron iteration. Hoy: todos los clients · futuro:
    filtrar por client_plans.status=active o similar cuando se defina."""
    try:
        r = _sb().table("clients").select("id").execute()
        return [str(row["id"]) for row in (r.data or [])]
    except Exception as e:
        logger.error(f"fetch_active_client_ids failed: {e}", exc_info=True)
        return []
