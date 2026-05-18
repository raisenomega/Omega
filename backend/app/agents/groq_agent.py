"""
Groq Agent - Ultra-fast LLM inference with Llama models
Filosofía: No velocity, only precision 🐢💎
"""
import os
import logging
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)


class GroqAgent:
    """Agent for ultra-fast LLM inference using Groq API"""

    MODELS = {
        "fast": "llama-3.1-8b-instant",  # Ultra fast for hashtags
        "versatile": "llama-3.3-70b-versatile",  # Best for prompt optimization
        "long_context": "mixtral-8x7b-32768"  # Long context for analysis
    }

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.default_model = self.MODELS["versatile"]

    async def execute(
        self,
        prompt: str,
        model: str = "versatile",
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> dict:
        """
        Execute prompt with Groq ultra-fast inference

        Args:
            prompt: User prompt
            model: Model key (fast, versatile, long_context) or full model name
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            dict with text, model, tokens_used, status
        """
        try:
            # Resolve model name
            model_name = self.MODELS.get(model, model)

            logger.info(f"GroqAgent: Executing with model {model_name}")

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Call Groq API
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(f"GroqAgent: Generated {tokens_used} tokens with {model_name}")

            return {
                "text": text,
                "model": model_name,
                "tokens_used": tokens_used,
                "status": "success",
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            logger.error(f"GroqAgent failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "model": model_name if 'model_name' in locals() else "unknown"
            }

    async def optimize_prompt(self, user_prompt: str) -> dict:
        """Optimize a user prompt for better AI generation"""
        system_prompt = """You are a prompt engineering expert. Optimize the user's prompt to be:
1. More specific and detailed
2. Better structured
3. Include relevant context
4. Follow best practices for AI generation

Return ONLY the optimized prompt, no explanation."""

        return await self.execute(
            prompt=user_prompt,
            model="versatile",
            system_prompt=system_prompt,
            max_tokens=500
        )

    async def generate_hashtags(
        self,
        content: str,
        niche: str,
        count: int = 30
    ) -> dict:
        """Ultra-fast hashtag generation"""
        prompt = f"""Generate {count} relevant hashtags for this social media post.

NICHE: {niche}
CONTENT: {content}

Return only hashtags separated by spaces, no explanations."""

        return await self.execute(
            prompt=prompt,
            model="fast",  # Ultra fast model
            max_tokens=200,
            temperature=0.8
        )

    async def adapt_content(
        self,
        content: str,
        from_platform: str,
        to_platform: str
    ) -> dict:
        """Adapt content from one platform to another"""
        prompt = f"""Adapt this {from_platform} content for {to_platform}.
Adjust tone, length, and formatting appropriately.

ORIGINAL ({from_platform}):
{content}

Return ONLY the adapted content for {to_platform}."""

        return await self.execute(
            prompt=prompt,
            model="versatile",
            max_tokens=800
        )
