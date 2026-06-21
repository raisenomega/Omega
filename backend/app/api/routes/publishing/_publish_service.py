"""Service · auto-publicacion real de un scheduled_post YA aprobado, via Zernio.

Flujo (best-effort · cero fabricacion):
  1. Carga el post + valida ownership (client) + status publicable ('pending').
  2. Resuelve la plataforma (social_account) y la cuenta Zernio (resolver 2a).
  3. POST real a Zernio (via zernio_adapter.create_post).
  4. Exito → status='published' + platform_post_id · Fallo REAL → status='failed'. JAMAS finge exito.

LINEA DIVISORIA config-vs-fallo (decision owner · NO mezclar):
  - TODO lo PREVIO a mark_publishing (sin red · media faltante · resolver cuenta 0/2+ · key ausente)
    = config/precondicion → PublishGateError (409 · el post QUEDA 'pending', reintentable apenas se
    conecta/corrige). NO se marca failed: "no se pudo intentar aun por config".
  - SOLO el intento REAL de publicacion (create_post: Zernio rechaza, transporte) → mark_failed:
    "se intento y no salio". Excepcion: media faltante → failed (el post no puede salir en esa red).

SAFETY (P2/P3/P4): NO genera ni aprueba contenido · unico estado publicable 'pending' (humano ya
aprobo) · cuenta ambigua (2+) NUNCA se adivina (resolver 2a · protege la marca del cliente).
"""
import asyncio
import logging
from typing import NamedTuple, Optional

from app.api.routes.publishing import _publish_repository as repo
from app.api.routes.publishing._media_guard import aspect_error, fetch_image_ratio, needs_ratio_check
from app.bc_cognition.infrastructure.zernio_adapter import ZernioError, create_post, _media_type
from app.bc_cognition.infrastructure.zernio_resolver import resolve_account_id
from app.api.routes.clients_v3._clients_reader import get_zernio_account_id  # F5/2b · mapeo per-negocio

logger = logging.getLogger(__name__)

_PUBLISHABLE_STATUS = "pending"
# Redes que exigen media (validacion de PRESENCIA · IG=imagen, TikTok=video). La validacion de TIPO
# la hace Zernio (si la media no sirve, lo rechaza → mark_failed honesto · decision owner #3).
_MEDIA_REQUIRED = {"instagram", "tiktok"}
# Tope de reintentos para fallos TRANSITORIOS de Zernio (5xx/429/timeout · Gap-1 resiliencia SPOF).
# Constante local (resiliencia operativa, NO guardrail de negocio → no entra en limits_omega).
MAX_RETRIES = 3


class PublishGateError(Exception):
    """Precondicion/config faltante · el handler mapea a 4xx · el post QUEDA 'pending' (reintentable).
    code ∈ {post_not_found, post_access_denied, post_not_publishable:<status>, sin_red,
            zernio_sin_cuenta:<plat>, zernio_cuenta_ambigua:<plat>:<n>, zernio_api_key_ausente, ...}."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class PublishResult(NamedTuple):
    published: bool
    platform_post_id: Optional[str] = None
    error: Optional[str] = None


async def publish_scheduled_post(scheduled_post_id: str, client_id: str) -> PublishResult:
    """Publica de verdad un post aprobado via Zernio. PublishGateError (4xx · queda pending) en
    precondicion/config · PublishResult(published=False, error) si el intento real de publicar falla."""
    post = await asyncio.to_thread(repo.get_scheduled_post, scheduled_post_id)
    if not post:
        raise PublishGateError("post_not_found")
    if str(post.get("client_id") or "") != client_id:
        raise PublishGateError("post_access_denied")
    if str(post.get("status") or "") != _PUBLISHABLE_STATUS:
        # gate intacto: solo 'pending' (aprobado) · un post que volvio de un 409 sigue pending → reintentable
        raise PublishGateError(f"post_not_publishable:{post.get('status')}")

    sa_id = post.get("social_account_id")
    platform = await asyncio.to_thread(repo.get_account_platform, str(sa_id)) if sa_id else None
    if not platform:
        raise PublishGateError("sin_red")  # post sin red asociada (estructural · queda pending)

    content_id = post.get("content_id")
    message = await asyncio.to_thread(repo.get_content_text, str(content_id)) if content_id else ""
    media_url = post.get("media_url")
    if platform in _MEDIA_REQUIRED and not media_url:
        # media faltante = el post NO puede salir en esta red → fallo real del post → failed honesto.
        err = f"zernio_media_requerida:{platform}"
        await asyncio.to_thread(repo.mark_failed, scheduled_post_id, err)
        return PublishResult(published=False, error=err)

    # Guard aspect ratio per-plataforma (autoridad: la red, NO Zernio). Cierra el zernio_400 enganoso
    # ("requires media content") cuando la imagen es vertical pero la red exige feed (IG: [0.8, 1.91]).
    # Solo imagenes (no video) · solo redes con rango de feed · fail-open si no se puede medir el ratio.
    # Per-fila: esta fila falla honesto; las demas del fan-out (TikTok/FB) publican normal (no se abortan).
    if media_url and needs_ratio_check(platform) and _media_type(str(media_url)) == "image":
        ratio = await fetch_image_ratio(str(media_url))
        if ratio is not None:
            ar_err = aspect_error(platform, ratio)
            if ar_err:
                await asyncio.to_thread(repo.mark_failed, scheduled_post_id, ar_err)
                return PublishResult(published=False, error=ar_err)

    # CONFIG (NO fallo real · ANTES de mark_publishing): resolver la cuenta Zernio. 0/2+ cuentas o key
    # ausente o no se pudo consultar → PublishGateError (409 · el post QUEDA 'pending', reintentable).
    # NO mark_failed: el intento de publicar aun NO se hizo (no se mata un post bueno por config faltante).
    try:
        mapped = await asyncio.to_thread(get_zernio_account_id, client_id, platform)  # F5/2b
        account_id = await resolve_account_id(platform, mapped)
    except ZernioError as e:
        raise PublishGateError(str(e))

    # ── A PARTIR DE ACA el intento de publicacion es REAL → un fallo va a mark_failed ──
    await asyncio.to_thread(repo.mark_publishing, scheduled_post_id)
    try:
        platform_post_id = await create_post(
            content=message,
            platforms=[{"platform": platform, "accountId": account_id}],
            publish_now=True,
            media_urls=[str(media_url)] if media_url else None,
        )
    except ZernioError as e:
        # TRANSITORIO (5xx/429/timeout) y aún hay margen → vuelve a 'pending', REX reintenta al próximo
        # tick (sin perder el post). TERMINAL (4xx/media) o tope agotado → mark_failed honesto como hoy.
        attempts = int(post.get("attempts") or 0) + 1
        if getattr(e, "transient", False) and attempts < MAX_RETRIES:
            logger.warning(f"auto-publish transient · post={scheduled_post_id} intento={attempts}/{MAX_RETRIES} · {e}")
            await asyncio.to_thread(repo.mark_retry, scheduled_post_id, attempts, str(e))
            return PublishResult(published=False, error=f"retry:{e}")
        logger.warning(f"auto-publish failed · post={scheduled_post_id} client={client_id} · {e}")
        await asyncio.to_thread(repo.mark_failed, scheduled_post_id, str(e))
        return PublishResult(published=False, error=str(e))
    except Exception as e:  # noqa: BLE001 · inesperado → honesto, nunca finge exito
        logger.error(f"auto-publish unexpected · post={scheduled_post_id} · {e}", exc_info=True)
        await asyncio.to_thread(repo.mark_failed, scheduled_post_id, f"unexpected:{type(e).__name__}")
        return PublishResult(published=False, error=f"unexpected:{type(e).__name__}")

    await asyncio.to_thread(repo.mark_published, scheduled_post_id, platform_post_id)
    logger.info(f"auto-publish OK · post={scheduled_post_id} client={client_id} platform={platform} id={platform_post_id}")
    return PublishResult(published=True, platform_post_id=platform_post_id)
