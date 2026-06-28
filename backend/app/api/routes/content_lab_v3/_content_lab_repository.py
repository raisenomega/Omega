"""Repository content_lab_v3 · única capa de WRITE/READ a content_lab_generated."""
import asyncio
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


async def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"content_lab_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def find_client_for_user(user_id: str) -> Optional[dict[str, Any]]:
    """Cliente propio del usuario (incluye industry + brand_voice)."""
    r = _sb().table("clients").select("id, name, industry, brand_voice, target_audience").eq("user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def find_client_context(client_id: str) -> dict[str, Any]:
    """Carga client_context RICO para el guion (qué ofrece, diferenciador, a quién, temas, evitar).
    DEBT-CAROUSEL-THIN-CONTEXT · campos relevantes, NO las 30 columnas (el cerebro trunca por campo)."""
    r = _sb().table("client_context").select(
        "tone, brand_voice, target_audience, audience_age_range, primary_goal, "
        "business_what, business_diff, business_to_whom, content_themes, "
        "avoided_topics, avoided_words, custom_instructions"
    ).eq("client_id", client_id).limit(1).execute()
    return r.data[0] if r.data else {}


def find_client_logo_url(client_id: str) -> Optional[str]:
    """URL del logo del cliente · client_brand_assets.logo_file_id → brand_files.storage_url.
    None si no tiene logo (la imagen sale sin marca)."""
    a = _sb().table("client_brand_assets").select("logo_file_id").eq("client_id", client_id).limit(1).execute()
    logo_id = a.data[0]["logo_file_id"] if a.data else None
    if not logo_id:
        return None
    f = _sb().table("brand_files").select("storage_url").eq("id", logo_id).limit(1).execute()
    return f.data[0].get("storage_url") if f.data else None


def find_client_brand_palette(client_id: str) -> dict[str, Any]:
    """A6 · paleta de marca del cliente · client_brand_assets (SOLO los 3 colores · NO fuentes/logo).
    {} si no hay fila (cliente sin paleta · el prompt sale sin marca). Hex limpio (#rrggbb · NO normaliza)."""
    r = _sb().table("client_brand_assets").select(
        "primary_color, secondary_color, accent_color"
    ).eq("client_id", client_id).limit(1).execute()
    return r.data[0] if r.data else {}


def insert_generated_content(client_id: str, payload: dict[str, Any]) -> Optional[str]:
    """INSERT content_lab_generated · retorna id del nuevo draft."""
    r = _sb().table("content_lab_generated").insert({**payload, "client_id": client_id}).execute()
    return str(r.data[0]["id"]) if r.data else None


def find_client_plan(client_id: str) -> str:
    """Retorna 'adopcion'|'basic'|'pro'|'enterprise' · default 'adopcion' si no row."""
    r = _sb().table("client_plans").select("plan").eq("client_id", client_id).limit(1).execute()
    return r.data[0]["plan"] if r.data else "adopcion"
