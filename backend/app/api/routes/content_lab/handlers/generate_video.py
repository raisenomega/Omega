"""
Handler: Generate Video with Runway Gen-3 Alpha Turbo
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.client_context_repository import ClientContextRepository
from app.agents.runway_agent import RunwayAgent

logger = logging.getLogger(__name__)


async def handle_generate_video_runway(
    account_id: str,
    prompt: str,
    duration: int = 5,
    style: str = "realistic"
) -> Dict[str, Any]:
    """
    Generate video using Runway Gen-3 Alpha Turbo

    Workflow:
    1. Get client_id from account_id
    2. Load client_context for prompt enrichment
    3. Enrich prompt with brand voice and context
    4. Call RunwayAgent to generate video
    5. Save to content_lab_generated
    6. Return video URL + metadata

    Args:
        account_id: Social account UUID
        prompt: Video description
        duration: Video duration (5 or 10 seconds)
        style: Video style (realistic, cinematic, animated)

    Returns:
        Dict with generated_text (video_url), content_type, provider, model

    Raises:
        HTTPException 404: Account not found
        HTTPException 500: Video generation failed
    """
    try:
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

        logger.info(f"Generating video for client {client_id}, plan: {plan}")

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
                enriched_prompt += ", cinematic lighting, professional production"
            elif style == "animated":
                enriched_prompt += ", smooth animation, vibrant colors"
            elif style == "realistic":
                enriched_prompt += ", photorealistic, high quality"

            logger.info(f"Enriched prompt: {enriched_prompt}")

        # 4. Generate video with RunwayAgent
        runway = RunwayAgent()
        result = await runway.execute(
            prompt=enriched_prompt,
            duration=duration,
            ratio="1280:768"
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
            "provider": "runway",
            "model": result.get("model", "gen3a_turbo"),
            "tokens_used": 0,  # Runway doesn't use tokens
            "is_saved": False,
            "is_active": True
        }

        save_resp = supabase.client.table("content_lab_generated")\
            .insert(content_data)\
            .execute()

        logger.info(f"Video saved to DB: {save_resp.data[0]['id']}")

        # 6. Return response (flat format like generate_image)
        return {
            "generated_text": video_url,
            "content_type": "video",
            "provider": "runway",
            "model": result.get("model", "gen3a_turbo"),
            "cached": False,
            "tokens_used": 0,
            "duration": duration,
            "ratio": result.get("ratio", "1280:768"),
            "task_id": result.get("task_id"),
            "original_prompt": prompt,
            "enriched_prompt": enriched_prompt
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
