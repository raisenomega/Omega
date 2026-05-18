"""
Handler: NOVA Chat with Claude Sonnet 4.6 (Anthropic)
Conversational AI assistant for OMEGA Company with agent memory
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging
import os
import re

from app.infrastructure.supabase_service import get_supabase_service
from ._agent_routing import detect_agent_mention, route_to_agent
from ._context_builder import build_nova_system_prompt, get_client_context
from ._memory_handler import extract_mentioned_agents, save_conversation_memory_async
from ._chat_helpers import ChatMessage, ChatRequest, extract_active_client

logger = logging.getLogger(__name__)


async def handle_chat(request: ChatRequest) -> Dict[str, Any]:
    """Process chat with Claude Sonnet 4.6 + multi-agent routing + memory"""
    try:
        messages = []
        for msg in request.messages[-20:]:
            if msg.role in ["user", "assistant"]:
                messages.append({"role": msg.role, "content": msg.content})

        # AGENT ROUTING: Check if user mentions specific agent
        if messages and messages[-1]["role"] == "user":
            mentioned_agent = detect_agent_mention(messages[-1]["content"])
            if mentioned_agent and mentioned_agent != "NOVA":
                logger.info(f"Routing to agent: {mentioned_agent}")
                active_client_name = extract_active_client(messages)
                active_client_id = None

                if not active_client_name:
                    try:
                        supabase = get_supabase_service()
                        memory_resp = supabase.client.table("agent_memory")\
                            .select("value").eq("agent_code", "NOVA")\
                            .order("created_at", desc=True).limit(5).execute()
                        for mem in (memory_resp.data or []):
                            val = mem.get("value", "")
                            match = re.search(
                                r"(?:hoy trabajamos|trabajamos con|activa|cliente activo[:\s]+)\s*(.+)",
                                val, re.IGNORECASE,
                            )
                            if match:
                                active_client_name = re.sub(r'[.!?,;]$', '', match.group(1).strip())
                                break
                    except Exception as e:
                        logger.warning(f"Could not check memory for active client: {e}")

                if active_client_name:
                    _, active_client_id, _ = await get_client_context(active_client_name)
                    active_client_id = active_client_id if active_client_id and str(active_client_id).strip() else None

                try:
                    supabase = get_supabase_service()
                    agent_info = supabase.client.table("omega_agents")\
                        .select("name,role,department,code").eq("code", mentioned_agent).limit(1).execute()
                    if agent_info.data:
                        info = agent_info.data[0]
                        system_prompt = (
                            f"Eres {mentioned_agent} ({info.get('name', mentioned_agent)}), "
                            f"{info.get('role', 'Agent')} del departamento de {info.get('department', 'Unknown')} "
                            f"en OMEGA Company (Raisen Agency). Responde SIEMPRE en español. Sé profesional, conciso y preciso."
                        )
                    else:
                        system_prompt = f"Eres {mentioned_agent} de OMEGA Company. Responde en español."
                except Exception as e:
                    logger.warning(f"Could not load agent info for {mentioned_agent}: {e}")
                    system_prompt = f"Eres {mentioned_agent} de OMEGA Company. Responde en español."

                return await route_to_agent(mentioned_agent, messages, system_prompt, 4096, client_id=active_client_id)

        # NOVA path
        context_text = ""
        if request.context_docs:
            context_text = "\n\nDOCUMENTOS DE CONTEXTO:\n"
            for doc in request.context_docs:
                context_text += f"\n--- {doc.get('name', 'Documento')} ---\n"
                context_text += doc.get('content', '')[:2000]

        if not messages or messages[0]["role"] != "user":
            messages.insert(0, {"role": "user", "content": "Hola NOVA, estoy listo para trabajar."})

        active_client_name = extract_active_client(messages)
        if active_client_name and not active_client_name.strip():
            active_client_name = None

        mentioned_agents = extract_mentioned_agents(messages)
        enhanced_system = await build_nova_system_prompt(
            context_text, mentioned_agents, active_client=active_client_name or ""
        )

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not configured")
            return {
                "role": "assistant",
                "content": "⚠️ Lo siento, el servicio de IA no está configurado correctamente. "
                           "Por favor verifica que ANTHROPIC_API_KEY esté configurado en Railway.",
            }

        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-sonnet-4-6",
                        "max_tokens": 8192,
                        "temperature": 0.7,
                        "system": enhanced_system,
                        "messages": messages,
                    },
                )
                if response.status_code != 200:
                    logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                    if response.status_code == 401:
                        raise HTTPException(status_code=503, detail="Invalid Anthropic API key")
                    elif response.status_code == 429:
                        raise HTTPException(status_code=503, detail="Anthropic rate limit exceeded")
                    raise HTTPException(status_code=503, detail=f"Anthropic API error: {response.status_code}")

                data = response.json()
                assistant_message = data["content"][0]["text"]
                logger.info(f"NOVA chat: generated {len(assistant_message)} chars")

                if active_client_name:
                    actual_name, client_id, client_ctx = await get_client_context(active_client_name)
                    if actual_name and client_ctx:
                        assistant_message = (
                            f"🎯 Cliente activo: **{actual_name}** — "
                            f"Contexto cargado ({len(client_ctx)} chars). ¿Qué trabajamos hoy?\n\n"
                            + assistant_message
                        )

                user_message = messages[-1]["content"] if messages else ""
                await save_conversation_memory_async(user_message, assistant_message, messages)
                return {"role": "assistant", "content": assistant_message}

        except httpx.TimeoutException:
            logger.error("Anthropic API timeout")
            raise HTTPException(status_code=503, detail="AI service timeout - please try again")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NOVA chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
