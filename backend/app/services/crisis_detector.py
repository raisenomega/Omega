"""
Crisis Detector Service
Pure crisis detection and assessment logic
"""
from typing import List
from pydantic import BaseModel


class CrisisLevel(BaseModel):
    """Crisis severity level"""
    level: str  # "monitoring" | "alert" | "crisis" | "emergency"
    score: float  # 0.0 to 1.0
    triggers: List[str]


class CrisisSignals(BaseModel):
    """Crisis detection signals"""
    negative_comment_percentage: float  # 0.0 to 1.0
    complaint_velocity: float  # complaints per hour
    sentiment_drop: float  # drop from baseline
    reach_of_negative_content: int
    media_involvement: bool
    influencer_involvement: bool
    platform: str = "instagram"  # default value


class CrisisImpactAssessment(BaseModel):
    """Crisis impact assessment"""
    crisis_level: CrisisLevel
    estimated_reputation_damage: str  # "minimal" | "moderate" | "severe" | "critical"
    affected_platforms: List[str]
    estimated_recovery_time: str  # "days" | "weeks" | "months"
    brand_equity_impact: float  # -1.0 to 0.0
    requires_immediate_action: bool


class RecoveryStep(BaseModel):
    """Recovery action step"""
    step_number: int
    action: str
    responsible: str  # "agency" | "client" | "both"
    deadline: str  # "immediate" | "24h" | "48h" | "1week"
    success_metric: str


class CrisisDetector:
    """Service for crisis detection and assessment"""
    
    def __init__(self):
        self.thresholds = {
            "monitoring": 0.3,
            "alert": 0.5,
            "crisis": 0.7,
            "emergency": 0.9
        }
    
    def calculate_crisis_score(self, signals: CrisisSignals) -> float:
        """
        Calculate crisis severity score
        
        Args:
            signals: Crisis signals data
            
        Returns:
            Crisis score from 0.0 to 1.0
        """
        # Weighted scoring
        score = 0.0
        
        # Negative sentiment (30% weight)
        score += signals.negative_comment_percentage * 0.3
        
        # Complaint velocity (20% weight)
        # Normalize: 10+ complaints/hour = max score
        velocity_score = min(signals.complaint_velocity / 10.0, 1.0)
        score += velocity_score * 0.2
        
        # Sentiment drop (25% weight)
        score += signals.sentiment_drop * 0.25
        
        # Reach of negative content (15% weight)
        # Normalize: 10000+ reach = max score
        reach_score = min(signals.reach_of_negative_content / 10000.0, 1.0)
        score += reach_score * 0.15
        
        # Media involvement (5% weight)
        if signals.media_involvement:
            score += 0.05
        
        # Influencer involvement (5% weight)
        if signals.influencer_involvement:
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def classify_crisis_level(self, score: float) -> str:
        """
        Classify crisis level from score
        
        Args:
            score: Crisis score (0-1)
            
        Returns:
            Crisis level string
        """
        if score >= self.thresholds["emergency"]:
            return "emergency"
        elif score >= self.thresholds["crisis"]:
            return "crisis"
        elif score >= self.thresholds["alert"]:
            return "alert"
        else:
            return "monitoring"
    
    def estimate_recovery_time(
        self,
        damage: str,
        crisis_level: str
    ) -> str:
        """
        Estimate recovery time
        
        Args:
            damage: Reputation damage level
            crisis_level: Crisis severity level
            
        Returns:
            Recovery time estimate
        """
        if damage == "critical" or crisis_level == "emergency":
            return "months"
        elif damage == "severe" or crisis_level == "crisis":
            return "weeks"
        else:
            return "days"
    
    def requires_immediate_action(self, level: str) -> bool:
        """
        Determine if immediate action required
        
        Args:
            level: Crisis level
            
        Returns:
            True if immediate action needed
        """
        return level in ["crisis", "emergency"]
    
    def estimate_brand_equity_impact(
        self,
        crisis_score: float,
        reach: int
    ) -> float:
        """
        Estimate brand equity impact
        
        Args:
            crisis_score: Crisis severity score
            reach: Reach of negative content
            
        Returns:
            Impact score from -1.0 to 0.0
        """
        # Combine score and reach
        base_impact = -crisis_score
        
        # Amplify by reach
        if reach > 50000:
            base_impact *= 1.5
        elif reach > 10000:
            base_impact *= 1.2
        
        return max(-1.0, base_impact)


# Global instance
crisis_detector = CrisisDetector()
