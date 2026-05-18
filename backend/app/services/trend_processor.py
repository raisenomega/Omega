"""
Trend Processor Service
Pure trend analysis and virality prediction logic
"""
from typing import List, Dict
from pydantic import BaseModel


class TrendingTopic(BaseModel):
    """Trending topic information"""
    topic: str
    platform: str
    trend_score: float  # 0.0 to 1.0
    velocity: str  # "rising" | "peak" | "declining"
    estimated_lifespan: str  # "hours" | "days" | "weeks"
    relevant_hashtags: List[str]
    content_angle: str
    risk_level: str  # "safe" | "moderate" | "risky"
    audience_alignment: float  # 0.0 to 1.0


class ViralityPrediction(BaseModel):
    """Virality prediction for content"""
    content_description: str
    virality_score: float  # 0.0 to 1.0
    predicted_reach_multiplier: float
    key_success_factors: List[str]
    recommended_timing: str  # ISO datetime or "ASAP"
    platform_fit: Dict[str, float]  # {"instagram": 0.8, "tiktok": 0.9}
    risk_factors: List[str]


class TrendOpportunity(BaseModel):
    """Trend opportunity for client"""
    trend: TrendingTopic
    relevance_to_niche: float  # 0.0 to 1.0
    content_ideas: List[str]  # 3-5 concrete ideas
    urgency: str  # "act_now" | "this_week" | "next_week"
    effort_required: str  # "low" | "medium" | "high"
    potential_impact: str  # "low" | "medium" | "high" | "viral"


class TrendProcessor:
    """Service for trend analysis"""
    
    def calculate_trend_score(
        self,
        engagement_velocity: float,
        share_rate: float
    ) -> float:
        """
        Calculate trend score
        
        Args:
            engagement_velocity: Rate of engagement growth
            share_rate: Share/repost rate
            
        Returns:
            Trend score from 0.0 to 1.0
        """
        # Weighted combination
        score = (engagement_velocity * 0.6) + (share_rate * 0.4)
        return min(1.0, max(0.0, score))
    
    def estimate_lifespan(
        self,
        velocity: str,
        topic_type: str
    ) -> str:
        """
        Estimate trend lifespan
        
        Args:
            velocity: Trend velocity (rising/peak/declining)
            topic_type: Type of topic
            
        Returns:
            "hours" | "days" | "weeks"
        """
        # Fast-moving trends
        if velocity == "peak" and topic_type in ["meme", "challenge", "viral"]:
            return "hours"
        
        # Medium-term trends
        if velocity == "rising" or topic_type in ["event", "news"]:
            return "days"
        
        # Long-term trends
        return "weeks"
    
    def calculate_relevance(
        self,
        trend_keywords: List[str],
        niche_keywords: List[str]
    ) -> float:
        """
        Calculate trend relevance to niche
        
        Args:
            trend_keywords: Keywords from trend
            niche_keywords: Keywords from client niche
            
        Returns:
            Relevance score from 0.0 to 1.0
        """
        if not trend_keywords or not niche_keywords:
            return 0.0
        
        trend_set = set(k.lower() for k in trend_keywords)
        niche_set = set(k.lower() for k in niche_keywords)
        
        overlap = len(trend_set & niche_set)
        total = len(trend_set | niche_set)
        
        if total == 0:
            return 0.0
        
        return overlap / total
    
    def predict_virality_score(
        self,
        engagement_rate: float,
        share_potential: float,
        timing_score: float
    ) -> float:
        """
        Predict virality score
        
        Args:
            engagement_rate: Expected engagement rate
            share_potential: Share/viral potential
            timing_score: Timing quality score
            
        Returns:
            Virality score from 0.0 to 1.0
        """
        # Weighted combination
        score = (
            engagement_rate * 0.3 +
            share_potential * 0.5 +
            timing_score * 0.2
        )
        
        return min(1.0, max(0.0, score))
    
    def calculate_platform_fit(
        self,
        content_type: str,
        platforms: List[str]
    ) -> Dict[str, float]:
        """
        Calculate platform fit scores
        
        Args:
            content_type: Type of content
            platforms: List of platforms to evaluate
            
        Returns:
            Dictionary of platform fit scores
        """
        # Platform preferences by content type
        preferences = {
            "video": {
                "tiktok": 1.0,
                "instagram": 0.9,
                "youtube": 0.95,
                "facebook": 0.7,
                "twitter": 0.5,
                "linkedin": 0.3
            },
            "image": {
                "instagram": 1.0,
                "pinterest": 0.95,
                "facebook": 0.8,
                "twitter": 0.7,
                "linkedin": 0.6,
                "tiktok": 0.3
            },
            "text": {
                "twitter": 1.0,
                "linkedin": 0.9,
                "facebook": 0.7,
                "instagram": 0.5,
                "tiktok": 0.2
            }
        }
        
        content_prefs = preferences.get(content_type, {})
        
        result = {}
        for platform in platforms:
            result[platform] = content_prefs.get(platform, 0.5)
        
        return result
    
    def estimate_effort(
        self,
        content_complexity: str,
        resources_available: bool
    ) -> str:
        """
        Estimate effort required
        
        Args:
            content_complexity: Complexity level
            resources_available: Whether resources are available
            
        Returns:
            "low" | "medium" | "high"
        """
        if content_complexity == "simple" and resources_available:
            return "low"
        elif content_complexity == "complex" or not resources_available:
            return "high"
        else:
            return "medium"


# Global instance
trend_processor = TrendProcessor()
