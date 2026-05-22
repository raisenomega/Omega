"""Use case · BrandDNA read-through cache · refresh cron entry point.

DEBT-044 (Sprint 2) cerrada: persiste DNA en client_brand_dna · trigger SQL
invalida last_computed_at cuando corpus cambia · este módulo orquesta lectura
(tabla primero · recompute si stale o ausente) + función cron de refresh diario.

Llamado por: api/routes/content_lab_v3/handlers/generate_text (read) ·
main.py startup (cron brand_dna_refresh 3 AM diario).
"""
import logging
from datetime import datetime, timedelta, timezone

from app.bc_cognition.application._brand_dna_builder import build_brand_dna
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.infrastructure.brand_dna_repository import (
    fetch_active_client_ids, fetch_persisted_dna, upsert_persisted_dna,
)
from app.bc_cognition.infrastructure.brand_voice_corpus_repository import (
    fetch_recent_corpus,
)

logger = logging.getLogger(__name__)

_STALE_AFTER_HOURS = 24


def build_dna_for_client(client_id: str, limit: int = 20) -> BrandDNA:
    """Read-through cache · tabla primero · recompute si stale o ausente."""
    persisted = fetch_persisted_dna(client_id)
    if persisted and not _is_stale(persisted):
        return BrandDNA.from_dict(persisted["dna_jsonb"])
    return _recompute_and_persist(client_id, limit)


def _is_stale(persisted: dict) -> bool:
    last = persisted.get("last_computed_at")
    if last is None:
        return True
    try:
        dt = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
    except ValueError:
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt) > timedelta(hours=_STALE_AFTER_HOURS)


def _recompute_and_persist(client_id: str, limit: int) -> BrandDNA:
    corpus = fetch_recent_corpus(client_id, limit=limit)
    dna = build_brand_dna(corpus)
    upsert_persisted_dna(client_id, dna.to_dict(), len(corpus))
    return dna


async def refresh_all_brand_dna() -> None:
    """Cron 3am · recompute + persist DNA para todos los clients activos."""
    client_ids = fetch_active_client_ids()
    logger.info(f"brand_dna refresh start · {len(client_ids)} clients")
    ok, failed = 0, 0
    for cid in client_ids:
        try:
            _recompute_and_persist(cid, limit=20)
            ok += 1
        except Exception as e:
            logger.error(f"brand_dna refresh failed · client={cid}: {e}")
            failed += 1
    logger.info(f"brand_dna refresh done · ok={ok} failed={failed}")
