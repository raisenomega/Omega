"""Repository brand_voice_corpus · SELECT only (no writes desde V3 aún).

Patrón: función libre síncrona + singleton _sb() interno · DDD A1/A9.
Best-effort fetch: si Supabase falla, log + retorna [] (DNA débil mejor
que crash). Mismo patrón que api/routes/content_lab_v3/_content_lab_repository.
"""
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb():
    return get_supabase_service().client


def fetch_recent_corpus(client_id: str, limit: int = 20) -> list[dict]:
    """Últimas `limit` filas del corpus del cliente, ordenadas por recencia.

    Schema corpus: id, text, tone_tags, platform, engagement_score, source,
    created_at (ver supabase/migrations/00008_aria_intelligence_schema.sql).
    """
    try:
        r = (
            _sb().table("brand_voice_corpus")
            .select("id, text, tone_tags, platform, engagement_score, source, created_at")
            .eq("client_id", client_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return r.data or []
    except Exception as e:
        logger.error(
            f"brand_voice_corpus_repository.fetch_recent_corpus failed "
            f"for client_id={client_id}: {e}",
            exc_info=True,
        )
        return []
