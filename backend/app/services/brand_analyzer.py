"""
Brand Analyzer Service
Pure brand analysis and validation logic
"""
from typing import List
from pydantic import BaseModel
import re


class BrandProfile(BaseModel):
    """Brand voice profile for a client"""
    client_id: str
    brand_name: str
    tone: str  # "friendly" | "professional" | "bold" | "luxury" | "casual"
    personality_traits: List[str]  # ["innovative", "trustworthy", "playful"]
    forbidden_words: List[str]
    required_keywords: List[str]
    emoji_usage: str  # "never" | "minimal" | "moderate" | "heavy"
    formality_level: int  # 1-10
    sample_posts: List[str]


class BrandValidationResult(BaseModel):
    """Result of brand voice validation"""
    is_compliant: bool
    compliance_score: float  # 0.0 to 1.0
    violations: List[str]
    suggestions: List[str]
    revised_content: str | None


class ContentImprovement(BaseModel):
    """Content improvement result"""
    original: str
    improved: str
    changes_made: List[str]
    tone_alignment_score: float


class PlatformAdaptation(BaseModel):
    """Platform-adapted content"""
    platform: str
    adapted_content: str
    character_count: int
    platform_rules_applied: List[str]


class BrandAnalyzer:
    """Service for brand voice analysis and validation"""
    
    def __init__(self):
        self.formal_words = {
            'furthermore', 'moreover', 'nevertheless', 'consequently',
            'therefore', 'accordingly', 'subsequently', 'henceforth'
        }
        
        self.casual_words = {
            'yeah', 'nope', 'gonna', 'wanna', 'kinda', 'sorta',
            'cool', 'awesome', 'super', 'totally', 'literally'
        }
    
    def check_forbidden_words(
        self,
        content: str,
        forbidden: List[str]
    ) -> List[str]:
        """
        Check for forbidden words in content
        
        Args:
            content: Content to check
            forbidden: List of forbidden words
            
        Returns:
            List of forbidden words found
        """
        content_lower = content.lower()
        found = []
        
        for word in forbidden:
            if word.lower() in content_lower:
                found.append(word)
        
        return found
    
    def calculate_formality_score(self, content: str) -> float:
        """
        Calculate formality score of content
        
        Args:
            content: Content to analyze
            
        Returns:
            Formality score from 0.0 (very casual) to 1.0 (very formal)
        """
        words = set(content.lower().split())
        
        formal_count = len(words & self.formal_words)
        casual_count = len(words & self.casual_words)
        
        # Check for other formality indicators
        has_contractions = "'" in content or "'" in content
        has_exclamations = content.count('!') > 0
        
        # Calculate base score
        if formal_count + casual_count == 0:
            base_score = 0.5  # Neutral
        else:
            base_score = formal_count / (formal_count + casual_count)
        
        # Adjust for other indicators
        if has_contractions:
            base_score -= 0.1
        if has_exclamations:
            base_score -= 0.05
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, base_score))
    
    def detect_emoji_density(self, content: str) -> str:
        """
        Detect emoji usage density
        
        Args:
            content: Content to analyze
            
        Returns:
            "never" | "minimal" | "moderate" | "heavy"
        """
        # Simple emoji detection (Unicode ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+",
            flags=re.UNICODE
        )
        
        emojis = emoji_pattern.findall(content)
        emoji_count = len(emojis)
        word_count = len(content.split())
        
        if emoji_count == 0:
            return "never"
        
        ratio = emoji_count / max(word_count, 1)
        
        if ratio < 0.05:
            return "minimal"
        elif ratio < 0.15:
            return "moderate"
        else:
            return "heavy"
    
    def calculate_compliance_score(
        self,
        violations: List[str],
        total_checks: int
    ) -> float:
        """
        Calculate compliance score
        
        Args:
            violations: List of violations found
            total_checks: Total number of checks performed
            
        Returns:
            Compliance score from 0.0 to 1.0
        """
        if total_checks == 0:
            return 1.0
        
        violation_count = len(violations)
        score = 1.0 - (violation_count / total_checks)
        
        return max(0.0, min(1.0, score))
    
    def validate_required_keywords(
        self,
        content: str,
        required: List[str]
    ) -> List[str]:
        """
        Check for required keywords
        
        Args:
            content: Content to check
            required: List of required keywords
            
        Returns:
            List of missing required keywords
        """
        content_lower = content.lower()
        missing = []
        
        for keyword in required:
            if keyword.lower() not in content_lower:
                missing.append(keyword)
        
        return missing


# Global instance
brand_analyzer = BrandAnalyzer()
