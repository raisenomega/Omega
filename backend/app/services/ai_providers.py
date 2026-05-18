"""
Multi-AI Provider System — 7 Engines for Content Lab
Filosofía: No velocity, only precision 🐢💎
"""
import logging
import os
from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import httpx

logger = logging.getLogger(__name__)

class AIProviders:
    """Multi-AI provider system — 7 engines mapped to OMEGA directors."""

    DIRECTORS = {
        "NOVA": {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "description": "Claude Sonnet 4.5 — OMEGA Chief Director", "strengths": ["Long-form", "Analysis", "Strategy"]},
        "ATLAS": {"provider": "openai", "model": "gpt-4o", "description": "GPT-4o — Client Intelligence", "strengths": ["Structured data", "JSON"]},
        "LUNA": {"provider": "deepseek", "model": "deepseek-chat", "description": "Deepseek V3 — Research", "strengths": ["Research", "Technical content"]},
        "REX": {"provider": "openai", "model": "gpt-4o-mini", "description": "GPT-4o-mini — Fast & Cheap", "strengths": ["Speed", "Cost"], "default": True},
        "VERA": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "description": "Gemini 2.0 Flash — Multi-modal", "strengths": ["Multi-modal", "Creative"]},
        "KIRA": {"provider": "groq", "model": "llama-3.3-70b-versatile", "description": "Llama 3.3 70B via Groq — Ultra-fast", "strengths": ["Real-time", "Speed"]},
        "ORACLE": {"provider": "deepseek", "model": "deepseek-reasoner", "description": "Deepseek R1 — Deep Reasoning", "strengths": ["Complex reasoning", "Logic"]}
    }

    def __init__(self):
        """Initialize all AI clients."""
        self.anthropic = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.deepseek = AsyncOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq = AsyncOpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

    def get_default_director(self) -> str:
        return "REX"

    def list_directors(self) -> Dict[str, Dict[str, Any]]:
        return self.DIRECTORS

    async def generate(self, director: str, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 2000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate content using specified director's AI engine."""
        config = self.DIRECTORS.get(director)
        if not config:
            raise ValueError(f"Unknown director: {director}")
        provider = config["provider"]
        model = config["model"]
        logger.info(f"Generating with {director} ({provider}/{model})")
        try:
            if provider == "anthropic":
                return await self._anthropic_generate(model, prompt, system_prompt, max_tokens, temperature)
            elif provider == "openai":
                return await self._openai_generate(model, prompt, system_prompt, max_tokens, temperature)
            elif provider == "deepseek":
                return await self._deepseek_generate(model, prompt, system_prompt, max_tokens, temperature)
            elif provider == "gemini":
                return await self._gemini_generate(model, prompt, system_prompt, max_tokens, temperature)
            elif provider == "groq":
                return await self._groq_generate(model, prompt, system_prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Provider {provider} not implemented")
        except Exception as e:
            logger.error(f"Generation failed for {director}: {e}")
            raise

    async def _anthropic_generate(self, model: str, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Dict[str, Any]:
        # Debug logging for NOVA model issues
        try:
            response = await self.anthropic.messages.create(
                model=model, max_tokens=max_tokens, temperature=temperature,
                system=system_prompt or "", messages=[{"role": "user", "content": prompt}]
            )
            logger.info(f"✅ Anthropic OK: model={model}, chars={len(response.content[0].text)}")
            return {
                "content": response.content[0].text, "provider": "anthropic", "model": model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            logger.error(f"❌ Anthropic FAIL: model={model}, error={type(e).__name__}: {e}", exc_info=True)
            raise

    async def _openai_generate(self, model: str, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.openai.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temperature
        )
        return {
            "content": response.choices[0].message.content, "provider": "openai", "model": model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }

    async def _deepseek_generate(self, model: str, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.deepseek.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temperature
        )
        return {
            "content": response.choices[0].message.content, "provider": "deepseek", "model": model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }

    async def _gemini_generate(self, model: str, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Dict[str, Any]:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}",
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        return {
            "content": content, "provider": "gemini", "model": model,
            "tokens_used": data.get("usageMetadata", {}).get("totalTokenCount", 0)
        }

    async def _groq_generate(self, model: str, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.groq.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temperature
        )
        return {
            "content": response.choices[0].message.content, "provider": "groq", "model": model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
