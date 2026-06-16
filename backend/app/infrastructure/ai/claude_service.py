"""
Anthropic Claude Service
Handles all interactions with Claude API
"""
from typing import List, Optional, Dict, Any
import logging
from anthropic import AsyncAnthropic
from app.config import settings
from app.bc_cognition.domain.routing_table import MODEL_SONNET

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for Anthropic Claude API interactions"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = MODEL_SONNET
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate text using Claude.

        Args:
            prompt: User prompt
            system_message: System instructions
            temperature: Creativity (0-1)
            max_tokens: Maximum response length
            model: Override model id (e.g. from routing_table.resolve_model).
                   If None, falls back to self.model (claude-sonnet-4-6).

        Returns:
            Generated text
        """
        effective_model = model or self.model
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = await self.client.messages.create(
                model=effective_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else "",
                messages=messages
            )
            
            text = response.content[0].text
            logger.info(
                f"Generated text with Claude ({effective_model}): {len(text)} characters"
            )
            
            return text
            
        except Exception as e:
            logger.error(f"Claude text generation error: {e}")
            raise
    
    async def analyze_strategy(
        self,
        context: Dict[str, Any],
        goals: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and create content strategy
        
        Args:
            context: Business context and current state
            goals: Strategic goals
            constraints: Budget, time, resource constraints
            
        Returns:
            Strategic recommendations
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_strategy_prompt(
                context,
                goals,
                constraints or {}
            )
            
            system_message = (
                "You are a strategic social media consultant with expertise in "
                "content planning, audience engagement, and ROI optimization. "
                "Provide data-driven, actionable recommendations."
            )
            
            response = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=4096
            )
            
            # Parse response into structured format
            strategy = self._parse_strategy_response(response)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Claude strategy analysis error: {e}")
            raise
    
    def _build_strategy_prompt(
        self,
        context: Dict[str, Any],
        goals: List[str],
        constraints: Dict[str, Any]
    ) -> str:
        """Build comprehensive strategy prompt"""
        prompt_parts = [
            "# Social Media Strategy Analysis",
            "",
            "## Current Context:",
        ]
        
        for key, value in context.items():
            prompt_parts.append(f"- {key}: {value}")
        
        prompt_parts.extend([
            "",
            "## Goals:",
        ])
        
        for i, goal in enumerate(goals, 1):
            prompt_parts.append(f"{i}. {goal}")
        
        if constraints:
            prompt_parts.extend([
                "",
                "## Constraints:",
            ])
            for key, value in constraints.items():
                prompt_parts.append(f"- {key}: {value}")
        
        prompt_parts.extend([
            "",
            "## Required Output:",
            "1. Content themes (3-5 themes)",
            "2. Posting frequency per platform",
            "3. Content mix (% educational, entertainment, promotional)",
            "4. Best posting times",
            "5. Key performance indicators",
            "6. 30-day action plan",
            "",
            "Provide specific, actionable recommendations."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_strategy_response(
        self,
        response: str
    ) -> Dict[str, Any]:
        """Parse Claude response into structured strategy"""
        # Simple parsing - can be enhanced with structured output
        return {
            "raw_analysis": response,
            "generated_at": "now",
            "model": self.model
        }


# Global instance
claude_service = ClaudeService()
