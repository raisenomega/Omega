"""
Handler: Generate Video with Fal.ai (Kling, Hunyuan, Wan)
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.client_context_repository import ClientContextRepository
from app.agents.fal_video_agent import FalVideoAgent

logger = logging.getLogger(__name__)

# Temporarily disabled models due to timeout/availability issues
DISABLED_MODELS = ["hunyuan"]


async def handle_generate_video_fal(
    account_id: str,
    prompt: str,
    duration: int = 5,
    model: str = "kling",
    style: str = "realistic"
) -> Dict[str, Any]:
    """
    Generate video using Fal.ai models (Kling, Hunyuan, Wan)

    Workflow:
    1. Get client_id from account_id
    2. Load client_context for prompt enrichment
    3. Enrich prompt with brand voice and context
    4. Call FalVideoAgent to generate video
    5. Save to content_lab_generated
    6. Return video URL + metadata

    Args:
        account_id: Social account UUID
        prompt: Video description
        duration: Video duration in seconds (5 or 10)
        model: Fal model (kling, hunyuan, wan)
        style: Video style (realistic, cinematic, animated)

    Returns:
        Dict with generated_text (video_url), content_type, provider, model

    Raises:
        HTTPException 404: Account not found
        HTTPException 500: Video generation failed
    """
    try:
        # Check if model is disabled
        if model in DISABLED_MODELS:
            raise HTTPException(
                status_code=503,
                detail=f"Model '{model}' temporarily unavailable due to timeout issues. Use 'kling' instead."
            )

        supabase = get_supabase_service()

        # 1. Get client info from account_id
        account_resp = supabase.client.table("social_accounts")\
            .select("client_id, platform, clients!inner(name, plan)")\
            .eq("id", account_id)\
            .eq("is_active", True)\
            .limit(1)\
            .execute()

        if not account_resp.data or len(account_resp.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Social account {account_id} not found or inactive"
            )

        account = account_resp.data[0]
        client_id = account["client_id"]
        plan = account["clients"]["plan"] if account.get("clients") else "basico_97"

        logger.info(f"Generating Fal video for client {client_id}, model: {model}")

        # 2. Load client context for enrichment
        context_repo = ClientContextRepository(supabase)
        client_context = context_repo.find_by_client_id(client_id)

        # 3. Enrich prompt with context
        enriched_prompt = prompt

        if client_context and client_context.has_context():
            brand_style = ""
            if client_context.brand_voice:
                adjectives = client_context.brand_voice.get("adjectives", [])
                if adjectives:
                    brand_style = f", {', '.join(adjectives[:2])} style"

            tone_desc = f", {client_context.tone} tone" if client_context.tone else ""

            # Build enriched prompt
            enriched_prompt = f"{prompt}{brand_style}{tone_desc}"

            # Add style descriptor
            if style == "cinematic":
                enriched_prompt += ", cinematic quality, professional lighting"
            elif style == "animated":
                enriched_prompt += ", smooth animation, vibrant visuals"
            elif style == "realistic":
                enriched_prompt += ", photorealistic, high detail"

            logger.info(f"Enriched prompt: {enriched_prompt}")

        # 4. Generate video with FalVideoAgent
        fal = FalVideoAgent()
        result = await fal.execute(
            prompt=enriched_prompt,
            model=model,
            duration=duration,
            aspect_ratio="16:9"
        )

        if result.get("status") == "failed":
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

        video_url = result.get("video_url")

        if not video_url:
            raise HTTPException(
                status_code=500,
                detail="Video generation succeeded but no URL returned"
            )

        # 5. Save to content_lab_generated
        content_data = {
            "client_id": client_id,
            "social_account_id": account_id,
            "content_type": "video",
            "content": video_url,
            "provider": "fal",
            "model": result.get("model_id", model),
            "tokens_used": 0,
            "is_saved": False
        }

        save_resp = supabase.client.table("content_lab_generated")\
            .insert(content_data)\
            .execute()

        logger.info(f"Fal video saved to DB: {save_resp.data[0]['id']}")

        # 6. Return response (flat format)
        return {
            "generated_text": video_url,
            "content_type": "video",
            "provider": "fal",
            "model": result.get("model_id", model),
            "cached": False,
            "tokens_used": 0,
            "duration": duration,
            "aspect_ratio": result.get("aspect_ratio", "16:9"),
            "fal_model": model,
            "original_prompt": prompt,
            "enriched_prompt": enriched_prompt
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fal video generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
