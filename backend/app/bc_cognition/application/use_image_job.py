"""Use case · image background job orchestration · DEBT-IMAGE-ASYNC F2 (espejo de use_video_job).

POST handler (F3) llama create_image_job() → inserta row pending + asyncio.create_task in-process
(mismo worker uvicorn · cero APScheduler · igual que video desde el 23 may). _run_image_job hace
running → generate_image_compat (~48s Gemini + upload) → overlay logo opcional → insert content →
DEBITA crédito → mark completed.

CRÍTICO (P1 facturación): el débito va SOLO al llegar a 'completed' (entregado) · NUNCA al iniciar ·
NUNCA en 'failed'. Cualquier excepción ANTES del débito salta al except → mark_failed → el débito
NO corre. try/except anti-orphan (igual que video): ninguna excepción deja el job colgado en 'running'.

NO duplica cobro con el path síncrono: en F3 el flag IMAGE_ASYNC_ENABLED enruta a UN solo path
(ON → este worker debita · OFF → handler síncrono debita). En F2 este worker aún no está cableado.
"""
import asyncio
import logging
from typing import Any, Optional

from app.api.routes.content_lab_v3 import _content_lab_repository as cl_repo
from app.bc_billing.application.credits_service import debit
from app.bc_billing.domain.credit_costs import cost_for_image
from app.bc_cognition.infrastructure import image_job_repository as repo
from app.bc_cognition.infrastructure._image_compat import generate_image_compat
from app.bc_cognition.infrastructure._logo_overlay import overlay_logo
from app.bc_cognition.infrastructure._storage_uploader import upload_image_bytes

logger = logging.getLogger(__name__)

# Ref fuerte a tasks activas · evita GC mid-execution (igual que use_video_job)
_active_tasks: set[asyncio.Task] = set()


async def create_image_job(client_id: str, prompt: str, size: str, quality: str,
                           style: str, apply_logo: bool,
                           reference_images_b64: Optional[list[str]] = None) -> str:
    """Inserta row pending + lanza worker async in-process. refs van como arg EN MEMORIA
    (NO al DB · evita filas enormes con base64). Devuelve job_id al instante."""
    job_id = repo.insert_pending_job(client_id, prompt, size, quality,
                                     {"style": style, "apply_logo": apply_logo})
    task = asyncio.create_task(_run_image_job(job_id, reference_images_b64), name=f"ijob_{job_id}")
    _active_tasks.add(task)
    task.add_done_callback(_active_tasks.discard)
    return job_id


async def _run_image_job(job_id: str, reference_images_b64: Optional[list[str]]) -> None:
    """Background worker · NUNCA deja escapar excepciones (orphan en 'running')."""
    try:
        job = repo.fetch_job(job_id)
        if not job:
            logger.error(f"_run_image_job: job_id={job_id} not found")
            return
        repo.update_job_running(job_id)
        client_id, meta = str(job["client_id"]), (job.get("metadata") or {})
        urls = await generate_image_compat(
            prompt=job["prompt"], size=job["size"], quality=job["quality"],
            n=1, client_id=client_id, reference_images_b64=reference_images_b64,
        )
        image_url = urls[0]
        if meta.get("apply_logo"):
            logo_url = await asyncio.to_thread(cl_repo.find_client_logo_url, client_id)
            if logo_url:
                try:
                    overlaid = await asyncio.to_thread(overlay_logo, image_url, logo_url)
                    image_url = await upload_image_bytes(overlaid, "image/png", client_id)
                except Exception as e:  # noqa: BLE001 · overlay best-effort · imagen sin marca
                    logger.warning(f"logo overlay falló · job={job_id}: {e}")
        # DEBT-CL-010 · re-check cancel mid-flight: NO persistir NI debitar si el user canceló
        current = repo.fetch_job(job_id)
        if current and current.get("status") == "cancelled":
            logger.info(f"image job {job_id} cancelled mid-flight · skip persist + skip débito")
            return
        content_id = await cl_repo.safe_insert(
            "insert_image_async", cl_repo.insert_generated_content, client_id, {
                "agent_code": "content_creator", "content_type": "image",
                "prompt": job["prompt"], "generated_text": image_url,
                "metadata": {"model": "nano-banana-2", "provider": "google",
                             "style": meta.get("style"), "ui_type": "image"},
                "confidence": 8, "status": "draft", "compliance_passed": True,
            },
        )
        # ── DÉBITO · SOLO acá ('completed' · entregado) · NUNCA al iniciar · NUNCA en 'failed' ──
        if content_id:
            await debit(client_id, "content_creator", cost_for_image("default"), "nano-banana", content_id)
        repo.update_job_completed(job_id, image_url, {"content_id": content_id, "style": meta.get("style")})
    except Exception as e:
        logger.exception(f"_run_image_job uncaught · job_id={job_id}")
        try:
            repo.update_job_failed(job_id, f"uncaught: {type(e).__name__}: {str(e)[:400]}")
        except Exception:
            logger.error(f"_run_image_job: ALSO failed update_failed · job_id={job_id} · ORPHAN")


def get_image_job(job_id: str) -> Optional[dict[str, Any]]:
    """Lee state · handler hace ownership check vs client propio."""
    return repo.fetch_job(job_id)
