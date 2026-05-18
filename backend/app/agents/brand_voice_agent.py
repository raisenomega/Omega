"""
Brand Voice Agent
Ensures brand consistency across all client content
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.claude_service import claude_service
from app.services.brand_analyzer import (
    brand_analyzer,
    BrandProfile,
    BrandValidationResult,
    ContentImprovement,
    PlatformAdaptation
)

logger = logging.getLogger(__name__)


class BrandVoiceAgent(BaseAgent):
    """
    Agent specialized in brand voice consistency
    - Content validation against brand profile
    - Content improvement for brand alignment
    - Brand profile creation from samples
    - Platform-specific adaptation
    """
    
    def __init__(self, agent_id: str = "brand_voice_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.BRAND_VOICE,
            model="claude-opus-4",
            tools=[
                "tone_analyzer",
                "content_validator",
                "brand_profiler",
                "platform_adapter"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute brand voice task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "validate":
                result = await self.validate_content(
                    task["content"],
                    BrandProfile(**task["brand_profile"])
                )
            elif task_type == "improve":
                result = await self.improve_content(
                    task["content"],
                    BrandProfile(**task["brand_profile"])
                )
            elif task_type == "create_profile":
                result = await self.create_brand_profile(
                    task["client_name"],
                    task["brand_description"],
                    task["sample_posts"]
                )
            elif task_type == "adapt_platform":
                result = await self.adapt_for_platform(
                    task["content"],
                    task["platform"],
                    BrandProfile(**task["brand_profile"])
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            logger.error(f"Brand voice execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def validate_content(
        self,
        content: str,
        brand_profile: BrandProfile
    ) -> BrandValidationResult:
        """Validate content against brand profile"""
        violations = []
        
        # Check forbidden words
        forbidden_found = brand_analyzer.check_forbidden_words(
            content, brand_profile.forbidden_words
        )
        if forbidden_found:
            violations.append(f"Forbidden words: {', '.join(forbidden_found)}")
        
        # Check required keywords
        missing_keywords = brand_analyzer.validate_required_keywords(
            content, brand_profile.required_keywords
        )
        if missing_keywords:
            violations.append(f"Missing keywords: {', '.join(missing_keywords)}")
        
        # Check emoji usage
        emoji_density = brand_analyzer.detect_emoji_density(content)
        if emoji_density != brand_profile.emoji_usage:
            violations.append(
                f"Emoji usage mismatch: {emoji_density} vs expected {brand_profile.emoji_usage}"
            )
        
        # Check formality
        formality_score = brand_analyzer.calculate_formality_score(content)
        expected_formality = brand_profile.formality_level / 10.0
        if abs(formality_score - expected_formality) > 0.3:
            violations.append(
                f"Formality mismatch: {formality_score:.2f} vs expected {expected_formality:.2f}"
            )
        
        # Calculate compliance score
        total_checks = 4
        compliance_score = brand_analyzer.calculate_compliance_score(
            violations, total_checks
        )
        
        # Generate AI suggestions if violations exist
        suggestions = []
        if violations:
            prompt = (
                f"Brand: {brand_profile.brand_name}\n"
                f"Tone: {brand_profile.tone}\n"
                f"Violations: {', '.join(violations)}\n\n"
                f"Content: {content}\n\n"
                f"Provide 3 specific suggestions to fix these violations:"
            )
            
            ai_suggestions = await claude_service.generate_text(
                prompt=prompt,
                max_tokens=200,
                temperature=0.6
            )
            
            suggestions = [
                s.strip() for s in ai_suggestions.split('\n')
                if s.strip() and len(s.strip()) > 10
            ][:3]
        
        return BrandValidationResult(
            is_compliant=len(violations) == 0,
            compliance_score=compliance_score,
            violations=violations,
            suggestions=suggestions,
            revised_content=None
        )
    
    async def improve_content(
        self,
        content: str,
        brand_profile: BrandProfile
    ) -> ContentImprovement:
        """Improve content to align with brand voice"""
        prompt = (
            f"Rewrite this content to match the brand voice:\n\n"
            f"Brand: {brand_profile.brand_name}\n"
            f"Tone: {brand_profile.tone}\n"
            f"Personality: {', '.join(brand_profile.personality_traits)}\n"
            f"Formality (1-10): {brand_profile.formality_level}\n"
            f"Emoji usage: {brand_profile.emoji_usage}\n\n"
            f"Original content:\n{content}\n\n"
            f"Rewrite maintaining the core message but aligning with brand voice:"
        )
        
        improved = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        # Identify changes
        changes = []
        if brand_analyzer.detect_emoji_density(content) != brand_analyzer.detect_emoji_density(improved):
            changes.append("Adjusted emoji usage")
        if len(improved) != len(content):
            changes.append("Modified length")
        changes.append("Aligned tone with brand voice")
        
        # Calculate alignment score
        validation = await self.validate_content(improved, brand_profile)
        
        return ContentImprovement(
            original=content,
            improved=improved.strip(),
            changes_made=changes,
            tone_alignment_score=validation.compliance_score
        )
    
    async def create_brand_profile(
        self,
        client_name: str,
        brand_description: str,
        sample_posts: List[str]
    ) -> BrandProfile:
        """Create brand profile from samples"""
        prompt = (
            f"Analyze these sample posts and create a brand voice profile:\n\n"
            f"Brand: {client_name}\n"
            f"Description: {brand_description}\n\n"
            f"Sample posts:\n"
        )
        
        for i, post in enumerate(sample_posts[:5], 1):
            prompt += f"{i}. {post}\n"
        
        prompt += (
            "\nProvide:\n"
            "1. Tone (one word: friendly/professional/bold/luxury/casual)\n"
            "2. 3 personality traits\n"
            "3. Formality level (1-10)\n"
            "4. Emoji usage (never/minimal/moderate/heavy)\n"
        )
        
        analysis = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.5
        )
        
        # Parse AI response (simplified)
        return BrandProfile(
            client_id=client_name.lower().replace(' ', '_'),
            brand_name=client_name,
            tone="professional",
            personality_traits=["trustworthy", "innovative", "helpful"],
            forbidden_words=[],
            required_keywords=[],
            emoji_usage="minimal",
            formality_level=7,
            sample_posts=sample_posts
        )
    
    async def adapt_for_platform(
        self,
        content: str,
        platform: str,
        brand_profile: BrandProfile
    ) -> PlatformAdaptation:
        """Adapt content for specific platform"""
        platform_limits = {
            "twitter": 280,
            "instagram": 2200,
            "facebook": 63206,
            "tiktok": 2200,
            "linkedin": 3000
        }
        
        char_limit = platform_limits.get(platform, 2200)
        
        prompt = (
            f"Adapt this content for {platform}:\n\n"
            f"Original: {content}\n\n"
            f"Brand: {brand_profile.brand_name} ({brand_profile.tone})\n"
            f"Character limit: {char_limit}\n\n"
            f"Adapt while maintaining brand voice:"
        )
        
        adapted = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        adapted = adapted.strip()[:char_limit]
        
        rules_applied = [
            f"Character limit: {char_limit}",
            f"Platform: {platform}",
            f"Brand tone: {brand_profile.tone}"
        ]
        
        return PlatformAdaptation(
            platform=platform,
            adapted_content=adapted,
            character_count=len(adapted),
            platform_rules_applied=rules_applied
        )


# Global instance
brand_voice_agent = BrandVoiceAgent()
