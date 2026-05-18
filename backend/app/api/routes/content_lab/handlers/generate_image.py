"""
Handler de generación/edición de imágenes para Content Lab.
- DALL-E 3: Generación desde cero
- FAL.ai Flux Kontext: Edición con imágenes base
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
import os
import fal_client
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.infrastructure._image_compat import generate_image_compat

logger = logging.getLogger(__name__)

async def handle_generate_image(
    account_id: str, prompt: str, style: str = "realistic", attachments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Handler HTTP para generación/edición de imágenes.
    - Si hay attachments → editar con FAL Flux Kontext
    - Sin attachments → generar con DALL-E 3
    """
    try:
        supabase = get_supabase_service()
        # 1. Obtener client info
        account_response = supabase.client.table("social_accounts")\
            .select("client_id, platform, clients!inner(name, plan)")\
            .eq("id", account_id)\
            .execute()
        if not account_response.data:
            raise HTTPException(404, f"Social account {account_id} not found")
        account = account_response.data[0]
        client_id = account["client_id"]
        client_name = account["clients"]["name"]

        # 2. Detectar si es edición o generación
        image_attachments = [a for a in (attachments or []) if a.get("type") == "image" or "base64" in a]
        if image_attachments:
            logger.info(f"Editing image for {client_name} with FAL Flux Kontext ({len(image_attachments)} images)")
            result = await _edit_with_fal_kontext(prompt, image_attachments, style)
        else:
            logger.info(f"Generating image for {client_name} with DALL-E 3")
            result = await _generate_with_dalle3(prompt, style)

        # 3. Guardar en DB
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

        logger.info(f"Image {result['mode']} for client {client_id} via {result['model']}")

        # 4. Retornar response en formato flat
        return {
            "generated_text": result["image_url"],
            "content_type": "image",
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "cached": False,
            "tokens_used": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, f"Error generando imagen: {str(e)}")

async def _edit_with_fal_kontext(prompt: str, images: List[Dict[str, Any]], style: str) -> Dict[str, Any]:
    """
    Edita imagen con FAL.ai Flux Kontext Pro.
    Soporta: agregar logos a fotos reales, modificar elementos, combinar imágenes.
    """
    # Configurar FAL key
    os.environ["FAL_KEY"] = os.getenv("FAL_KEY", "")

    # Validar que hay al menos una imagen
    if not images:
        logger.warning("No images provided for editing, falling back to DALL-E 3")
        return await _generate_with_dalle3(prompt, style)

    # Usar primera imagen como base
    first_image = images[0]
    base64_data = first_image.get("base64", "")

    if not base64_data:
        logger.warning("Empty base64 data, falling back to DALL-E 3")
        return await _generate_with_dalle3(prompt, style)

    # Remover prefijo data:image/xxx;base64, si existe
    if "," in base64_data:
        base64_data = base64_data.split(",", 1)[1]

    # Flux Kontext necesita data URI
    image_data_uri = f"data:image/png;base64,{base64_data}"

    # Construir prompt mejorado según estilo
    enhanced_prompt = _enhance_prompt(prompt, style)

    # Llamar FAL.ai Flux Kontext Pro
    try:
        result = await fal_client.run_async(
            "fal-ai/flux-pro/kontext",
            arguments={
                "prompt": enhanced_prompt,
                "image_url": image_data_uri,
                "guidance_scale": 3.5,
                "num_inference_steps": 28,
                "safety_tolerance": "2"
            }
        )

        if not result.get("images") or len(result["images"]) == 0:
            raise Exception("FAL Flux Kontext returned no images")

        image_url = result["images"][0]["url"]

        return {
            "image_url": image_url,
            "provider": "fal",
            "model": "flux-kontext-pro",
            "mode": "edit"
        }

    except Exception as e:
        logger.error(f"FAL Flux Kontext edit failed: {e}")
        # Fallback a Nano Banana si falla
        logger.warning("Falling back to Nano Banana generation")
        return await _generate_with_nano_banana(prompt, style)

async def _generate_with_nano_banana(prompt: str, style: str) -> Dict[str, Any]:
    """Generación nueva con Nano Banana (sin imágenes base · Fase 2 §2.4)"""
    enhanced_prompt = _enhance_prompt(prompt, style)
    try:
        image_urls = await generate_image_compat(
            prompt=enhanced_prompt, n=1, size="1024x1024", quality="standard"
        )
        if not image_urls:
            raise Exception("Nano Banana returned no images")
        return {"image_url": image_urls[0], "provider": "google", "model": "nano-banana-2", "mode": "generate"}
    except Exception as e:
        logger.error(f"Nano Banana generation failed: {e}")
        raise HTTPException(500, f"Nano Banana generation failed: {str(e)}")

def _enhance_prompt(prompt: str, style: str) -> str:
    """Mejora el prompt según el estilo solicitado"""
    style_suffixes = {
        "realistic": ", photorealistic, high quality, professional photography",
        "cartoon": ", cartoon style, vibrant colors, playful illustration",
        "minimal": ", minimalist design, clean lines, simple composition"
    }
    suffix = style_suffixes.get(style, style_suffixes["realistic"])
    enhanced = f"{prompt}{suffix}"
    # Flux Kontext limit: reasonable prompt length
    if len(enhanced) > 4000:
        max_prompt_len = 4000 - len(suffix)
        enhanced = f"{prompt[:max_prompt_len]}{suffix}"
    return enhanced
