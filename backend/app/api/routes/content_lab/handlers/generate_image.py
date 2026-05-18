"""
Handler de generación/edición de imágenes para Content Lab.
- Nano Banana 2 (Gemini Image): generación nueva + edición con reference images.

Filosofía: No velocity, only precision 🐢💎

Fase 2 §2.4: swap DALL-E 3 → Nano Banana (generación).
Fase 2 §2.6: swap FAL Flux Kontext (edit mode) → Nano Banana refs (DEBT-022 cerrada).
"""
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.infrastructure._image_compat import generate_image_compat

logger = logging.getLogger(__name__)


async def handle_generate_image(
    account_id: str,
    prompt: str,
    style: str = "realistic",
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Handler HTTP para generación/edición de imágenes con Nano Banana.
    - Si hay attachments → modo edit con reference_images_b64
    - Sin attachments → modo generate puro
    """
    try:
        supabase = get_supabase_service()
        account_response = supabase.client.table("social_accounts")\
            .select("client_id, platform, clients!inner(name, plan)")\
            .eq("id", account_id)\
            .execute()
        if not account_response.data:
            raise HTTPException(404, f"Social account {account_id} not found")
        account = account_response.data[0]
        client_id = account["client_id"]
        client_name = account["clients"]["name"]

        image_attachments = [
            a for a in (attachments or [])
            if a.get("type") == "image" or "base64" in a
        ]
        ref_b64 = _extract_reference_b64(image_attachments)

        mode = "edit" if ref_b64 else "generate"
        logger.info(
            f"{mode.capitalize()} image for {client_name} with Nano Banana "
            f"({len(ref_b64) if ref_b64 else 0} refs)"
        )
        result = await _generate_with_nano_banana(prompt, style, mode, ref_b64)

        try:
            supabase.client.table("content_lab_generated").insert({
                "client_id": client_id,
                "social_account_id": account_id,
                "content_type": "image",
                "content": result["image_url"],
                "provider": result["provider"],
                "model": result["model"],
                "tokens_used": 0,
            }).execute()
        except Exception as db_error:
            logger.warning(f"Failed to save image to DB: {db_error}")

        logger.info(
            f"Image {result['mode']} for client {client_id} via {result['model']}"
        )

        return {
            "generated_text": result["image_url"],
            "content_type": "image",
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "cached": False,
            "tokens_used": 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, f"Error generando imagen: {str(e)}")


def _extract_reference_b64(images: List[Dict[str, Any]]) -> Optional[List[str]]:
    """Extract clean base64 strings (sin data URI prefix) from attachments."""
    if not images:
        return None
    refs: List[str] = []
    for img in images:
        b64 = img.get("base64", "")
        if not b64:
            continue
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        refs.append(b64)
    return refs or None


async def _generate_with_nano_banana(
    prompt: str,
    style: str,
    mode: str,
    reference_images_b64: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate or edit image with Nano Banana (Fase 2 §2.4 + §2.6)."""
    enhanced_prompt = _enhance_prompt(prompt, style)
    try:
        image_urls = await generate_image_compat(
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            reference_images_b64=reference_images_b64,
        )
        if not image_urls:
            raise Exception("Nano Banana returned no images")
        return {
            "image_url": image_urls[0],
            "provider": "google",
            "model": "nano-banana-2",
            "mode": mode,
        }
    except Exception as e:
        logger.error(f"Nano Banana generation failed: {e}")
        raise HTTPException(500, f"Nano Banana generation failed: {str(e)}")


def _enhance_prompt(prompt: str, style: str) -> str:
    """Mejora el prompt según el estilo solicitado."""
    style_suffixes = {
        "realistic": ", photorealistic, high quality, professional photography",
        "cartoon": ", cartoon style, vibrant colors, playful illustration",
        "minimal": ", minimalist design, clean lines, simple composition",
    }
    suffix = style_suffixes.get(style, style_suffixes["realistic"])
    enhanced = f"{prompt}{suffix}"
    if len(enhanced) > 8000:
        max_prompt_len = 8000 - len(suffix)
        enhanced = f"{prompt[:max_prompt_len]}{suffix}"
    return enhanced
