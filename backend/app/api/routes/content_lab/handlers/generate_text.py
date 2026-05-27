"""
Handler de generación de texto para Content Lab.
Filosofía: No velocity, only precision 🐢💎
DDD: API Interface layer - thin orchestration over services.
Strict <200L per file.
"""
from typing import Any
from fastapi import HTTPException
import logging

from app.services.ai_providers import AIProviders
from app.infrastructure.supabase_service import get_supabase_service
from app.services.content_lab_context_service import ContentLabContextService
from app.services.content_lab_prompt_service import ContentLabPromptService
from ._generate_text_helpers import (
    CONTENT_TYPE_MAP, _lookup_client_and_account, _normalize_plan
)

logger = logging.getLogger(__name__)


async def handle_generate_text(
    account_id: str, content_type: str, brief: str,
    language: str = "es", director: str = "REX"
) -> dict:
    """
    Generates text using Prompt Vault + AI providers.
    Workflow: Load context → Select prompt → Generate → Save → Return
    """
    try:
        # Map organizational agents to AI Directors
        AGENT_TO_DIRECTOR = {
            "RAFA": "REX",  # RAFA (Content Creator) → REX (fast tier)
            "ATLAS": "ATLAS",  # Pass-through
            "NOVA": "NOVA"  # Pass-through
        }
        director_normalized = AGENT_TO_DIRECTOR.get(director.upper(), director.upper())

        # Normalize content_type
        content_type = CONTENT_TYPE_MAP.get(content_type, content_type)

        # Get Supabase client
        supabase = get_supabase_service()

        # 1. Obtener client_id y platform - intenta social_accounts, luego clients
        client_id, client_name, plan, platform, social_account_id = (
            _lookup_client_and_account(supabase, account_id)
        )

        # Normalize plan to match LLM_TIERS
        user_tier = _normalize_plan(plan)

        logger.info(
            f"Generating {content_type} for {client_name} ({user_tier}) - "
            f"brief: {brief[:50]}..."
        )

        # 2. Load client context + brand voice
        context_service = ContentLabContextService(supabase)
        context_data, audience, tone, keywords, brand_voice = (
            context_service.load_context_with_brand_voice(client_id)
        )

        # 3. Select and build prompts (vault vs default)
        prompt_service = ContentLabPromptService(supabase)
        vertical = context_data.get("business_type") or "generic"

        user_prompt, system_prompt, vault_used = (
            await prompt_service.select_and_build_prompts(
                content_type=content_type,
                vertical=vertical,
                platform=platform,
                brief=brief,
                client_name=client_name,
                audience=audience,
                tone=tone,
                language=language,
                goal="engagement",
                context_data=context_data,
                brand_voice=brand_voice,
                keywords=keywords
            )
        )

        # 4. Llamar al AI provider seleccionado (multi-engine)
        ai_providers = AIProviders()
        fallback_used = False
        original_director = director_normalized

        try:
            llm_response = await ai_providers.generate(
                director=director_normalized,
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=4096,
                temperature=0.7
            )
        except Exception as llm_error:
            # Fallback to REX if primary director fails
            logger.error(
                f"LLM generation failed for director={director_normalized}: {llm_error}",
                exc_info=True
            )
            if director_normalized != "REX":
                logger.warning(f"Falling back from {director_normalized} to REX (fast tier)")
                fallback_used = True
                director_normalized = "REX"
                llm_response = await ai_providers.generate(
                    director="REX",
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=4096,
                    temperature=0.7
                )
            else:
                # REX itself failed - no fallback available
                raise

        # 5. Guardar en DB (including vault_prompt_id for tracking)
        supabase.client.table("content_lab_generated").insert({
            "client_id": client_id,
            "social_account_id": social_account_id,
            "content_type": content_type,
            "content": llm_response["content"],
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "tokens_used": llm_response["tokens_used"],
            "vault_prompt_id": vault_used["id"] if vault_used else None
        }).execute()

        logger.info(
            f"Generated {content_type} for client {client_id} "
            f"via {director_normalized} ({llm_response['provider']}/{llm_response['model']})"
        )

        # 6. Ensure UTF-8 encoding (fix for "Â¡" corrupted chars)
        generated_text = llm_response["content"]
        if isinstance(generated_text, bytes):
            generated_text = generated_text.decode('utf-8', errors='replace')
        # Normalize unicode (NFC form for proper char representation)
        import unicodedata
        generated_text = unicodedata.normalize('NFC', generated_text)

        # 7. Retornar response en formato flat (with vault metadata + fallback info)
        response_data = {
            "generated_text": generated_text,
            "content_type": content_type,
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "director": director_normalized,
            "cached": False,
            "tokens_used": llm_response["tokens_used"],
            "vault_prompt_used": vault_used
        }

        # Add fallback metadata if fallback was used
        if fallback_used:
            response_data["fallback_used"] = True
            response_data["original_director"] = original_director
            response_data["fallback_reason"] = f"{original_director} unavailable"

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}", exc_info=True)
        raise HTTPException(500, f"Error generando contenido: {str(e)}")
