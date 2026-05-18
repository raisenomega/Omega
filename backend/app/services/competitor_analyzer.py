"""
Competitor Analyzer Service
Pure competitor analysis and benchmarking logic
"""
from typing import List, Dict
from pydantic import BaseModel


class CompetitorProfile(BaseModel):
    """Competitor profile"""
    competitor_name: str
    platform: str
    estimated_followers: int | None
    avg_engagement_rate: float | None
    posting_frequency: str  # "daily" | "3x_week" | "weekly" | "irregular"
    content_types: List[str]  # ["video", "carousel", "story", "reel"]
    top_hashtags: List[str]
    best_performing_topics: List[str]
    peak_posting_hours: List[int]  # Hours 0-23


class BenchmarkReport(BaseModel):
    """Benchmark comparison report"""
    client_name: str
    competitor_name: str
    client_metrics: Dict[str, float]
    competitor_metrics: Dict[str, float]
    performance_gaps: Dict[str, float]  # positive = client wins
    client_advantages: List[str]
    competitor_advantages: List[str]
    opportunities: List[str]


class ContentGapAnalysis(BaseModel):
    """Content gap analysis"""
    topics_only_competitor: List[str]
    topics_only_client: List[str]
    shared_topics: List[str]
    untapped_opportunities: List[str]
    recommended_content_pillars: List[str]
    estimated_opportunity_size: str  # "small" | "medium" | "large"


class CompetitorAnalyzer:
    """Service for competitor analysis"""
    
    def calculate_performance_gap(
        self,
        client: float,
        competitor: float
    ) -> float:
        """
        Calculate performance gap
        
        Args:
            client: Client metric value
            competitor: Competitor metric value
            
        Returns:
            Gap percentage (positive = client wins)
        """
        if competitor == 0:
            return 100.0 if client > 0 else 0.0
        
        gap = ((client - competitor) / competitor) * 100
        return round(gap, 2)
    
    def identify_content_overlap(
        self,
        client_topics: List[str],
        competitor_topics: List[str]
    ) -> Dict[str, List[str]]:
        """
        Identify content overlap and gaps
        
        Args:
            client_topics: Client's content topics
            competitor_topics: Competitor's content topics
            
        Returns:
            Dictionary with overlap analysis
        """
        client_set = set(t.lower() for t in client_topics)
        competitor_set = set(t.lower() for t in competitor_topics)
        
        shared = list(client_set & competitor_set)
        only_client = list(client_set - competitor_set)
        only_competitor = list(competitor_set - client_set)
        
        return {
            "shared": shared,
            "only_client": only_client,
            "only_competitor": only_competitor,
            "overlap_percentage": round(
                len(shared) / max(len(client_set), 1) * 100, 2
            )
        }
    
    def rank_opportunities(
        self,
        gaps: List[str],
        market_data: Dict[str, float]
    ) -> List[str]:
        """
        Rank opportunities by potential
        
        Args:
            gaps: List of content gaps
            market_data: Market size/interest data
            
        Returns:
            Ranked list of opportunities
        """
        # Simple ranking by market data
        ranked = []
        
        for gap in gaps:
            score = market_data.get(gap.lower(), 0.5)
            ranked.append((gap, score))
        
        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return [gap for gap, _ in ranked]
    
    def calculate_engagement_score(
        self,
        likes: int,
        comments: int,
        shares: int,
        followers: int
    ) -> float:
        """Calculate engagement score"""
        if followers == 0:
            return 0.0
        
        total_engagement = likes + (comments * 2) + (shares * 3)
        score = (total_engagement / followers) * 100
        
        return round(score, 2)
    
    def estimate_opportunity_size(
        self,
        gap_count: int,
        market_interest: float
    ) -> str:
        """
        Estimate opportunity size
        
        Args:
            gap_count: Number of content gaps
            market_interest: Market interest score (0-1)
            
        Returns:
            "small" | "medium" | "large"
        """
        combined_score = gap_count * market_interest
        
        if combined_score < 2:
            return "small"
        elif combined_score < 5:
            return "medium"
        else:
            return "large"


# Global instance
competitor_analyzer = CompetitorAnalyzer()
