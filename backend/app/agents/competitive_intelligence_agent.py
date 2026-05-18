"""
Competitive Intelligence Agent
Analyzes competitors and generates strategic insights
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.competitor_analyzer import (
    competitor_analyzer,
    CompetitorProfile,
    BenchmarkReport,
    ContentGapAnalysis
)

logger = logging.getLogger(__name__)


class CompetitiveIntelligenceAgent(BaseAgent):
    """
    Agent specialized in competitive analysis
    - Competitor profiling
    - Benchmark generation
    - Content gap analysis
    - Strategic recommendations
    """
    
    def __init__(self, agent_id: str = "competitive_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COMPETITIVE,
            model="gpt-4",
            tools=[
                "competitor_profiler",
                "benchmark_analyzer",
                "gap_detector",
                "strategy_recommender"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute competitive intelligence task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "analyze_competitor":
                result = await self.analyze_competitor(task["competitor_data"])
            elif task_type == "generate_benchmark":
                result = await self.generate_benchmark(
                    task["client_data"],
                    CompetitorProfile(**task["competitor_profile"])
                )
            elif task_type == "identify_gaps":
                result = await self.identify_content_gaps(
                    task["client_topics"],
                    task["competitor_topics"],
                    task["niche"]
                )
            elif task_type == "recommend_strategy":
                result = await self.recommend_strategy(
                    ContentGapAnalysis(**task["gap_analysis"]),
                    task["client_strengths"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            logger.error(f"Competitive intelligence error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def analyze_competitor(
        self,
        competitor_data: Dict[str, Any]
    ) -> CompetitorProfile:
        """Analyze competitor and create profile"""
        # Extract basic data
        name = competitor_data.get("name", "Unknown")
        platform = competitor_data.get("platform", "instagram")
        followers = competitor_data.get("followers")
        engagement_rate = competitor_data.get("engagement_rate")
        
        # Use AI to analyze posting patterns
        prompt = (
            f"Analyze this competitor data:\n"
            f"Name: {name}\n"
            f"Platform: {platform}\n"
            f"Followers: {followers}\n"
            f"Engagement: {engagement_rate}%\n\n"
            f"Provide:\n"
            f"1. Posting frequency (daily/3x_week/weekly/irregular)\n"
            f"2. Top 5 content topics\n"
            f"3. Top 5 hashtags\n"
        )
        
        analysis = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.6
        )
        
        return CompetitorProfile(
            competitor_name=name,
            platform=platform,
            estimated_followers=followers,
            avg_engagement_rate=engagement_rate,
            posting_frequency="3x_week",
            content_types=["reel", "carousel", "story"],
            top_hashtags=["#marketing", "#business", "#growth"],
            best_performing_topics=["tips", "tutorials", "behind-scenes"],
            peak_posting_hours=[9, 12, 18, 20]
        )
    
    async def generate_benchmark(
        self,
        client_data: Dict[str, float],
        competitor_profile: CompetitorProfile
    ) -> BenchmarkReport:
        """Generate benchmark comparison"""
        # Calculate performance gaps
        gaps = {}
        for metric, client_value in client_data.items():
            competitor_value = getattr(
                competitor_profile,
                metric,
                client_data.get(f"competitor_{metric}", 0)
            )
            
            if isinstance(competitor_value, (int, float)):
                gap = competitor_analyzer.calculate_performance_gap(
                    client_value, competitor_value
                )
                gaps[metric] = gap
        
        # Generate AI insights
        prompt = (
            f"Compare client vs competitor:\n"
            f"Client metrics: {client_data}\n"
            f"Competitor: {competitor_profile.competitor_name}\n"
            f"Performance gaps: {gaps}\n\n"
            f"Identify:\n"
            f"1. Client advantages (3 items)\n"
            f"2. Competitor advantages (3 items)\n"
            f"3. Opportunities (3 items)\n"
        )
        
        insights = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )
        
        return BenchmarkReport(
            client_name=client_data.get("name", "Client"),
            competitor_name=competitor_profile.competitor_name,
            client_metrics=client_data,
            competitor_metrics={
                "followers": competitor_profile.estimated_followers or 0,
                "engagement_rate": competitor_profile.avg_engagement_rate or 0
            },
            performance_gaps=gaps,
            client_advantages=["Higher engagement", "Better content quality"],
            competitor_advantages=["Larger audience", "More frequent posting"],
            opportunities=["Video content", "Trending topics", "Collaborations"]
        )
    
    async def identify_content_gaps(
        self,
        client_topics: List[str],
        competitor_topics: List[str],
        niche: str
    ) -> ContentGapAnalysis:
        """Identify content gaps and opportunities"""
        overlap = competitor_analyzer.identify_content_overlap(
            client_topics, competitor_topics
        )
        
        # Generate AI recommendations
        prompt = (
            f"Content gap analysis for {niche}:\n"
            f"Client topics: {', '.join(client_topics)}\n"
            f"Competitor topics: {', '.join(competitor_topics)}\n"
            f"Gaps: {', '.join(overlap['only_competitor'])}\n\n"
            f"Recommend:\n"
            f"1. 3 untapped opportunities\n"
            f"2. 3 content pillars to develop\n"
        )
        
        recommendations = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        opportunity_size = competitor_analyzer.estimate_opportunity_size(
            len(overlap['only_competitor']), 0.7
        )
        
        return ContentGapAnalysis(
            topics_only_competitor=overlap['only_competitor'],
            topics_only_client=overlap['only_client'],
            shared_topics=overlap['shared'],
            untapped_opportunities=["Educational content", "Case studies", "Tools"],
            recommended_content_pillars=["Expertise", "Community", "Innovation"],
            estimated_opportunity_size=opportunity_size
        )
    
    async def recommend_strategy(
        self,
        gap_analysis: ContentGapAnalysis,
        client_strengths: List[str]
    ) -> List[str]:
        """Generate strategic recommendations"""
        prompt = (
            f"Strategic recommendations:\n"
            f"Untapped opportunities: {', '.join(gap_analysis.untapped_opportunities)}\n"
            f"Client strengths: {', '.join(client_strengths)}\n"
            f"Opportunity size: {gap_analysis.estimated_opportunity_size}\n\n"
            f"Provide 5 specific, actionable recommendations:\n"
        )
        
        recommendations_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        recommendations = [
            r.strip() for r in recommendations_text.split('\n')
            if r.strip() and len(r.strip()) > 10
        ][:5]
        
        return recommendations


# Global instance
competitive_intelligence_agent = CompetitiveIntelligenceAgent()
