"""
Trend Hunter Agent
Identifies trends and predicts viral opportunities
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.trend_processor import (
    trend_processor,
    TrendingTopic,
    ViralityPrediction,
    TrendOpportunity
)

logger = logging.getLogger(__name__)


class TrendHunterAgent(BaseAgent):
    """
    Agent specialized in trend detection and virality prediction
    - Trend analysis
    - Virality prediction
    - Opportunity identification
    - Trend-based content generation
    """
    
    def __init__(self, agent_id: str = "trend_hunter_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.TREND_HUNTER,
            model="gpt-4",
            tools=[
                "trend_analyzer",
                "virality_predictor",
                "opportunity_finder",
                "trend_content_generator"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trend hunting task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "analyze_trends":
                result = await self.analyze_trends(
                    task["platform_data"],
                    task["client_niche"]
                )
            elif task_type == "predict_virality":
                result = await self.predict_virality(
                    task["content_description"],
                    task["platform"],
                    task["target_audience"]
                )
            elif task_type == "find_opportunities":
                result = await self.find_opportunities(
                    [TrendingTopic(**t) for t in task["trends"]],
                    task["client_niche"],
                    task["brand_profile"]
                )
            elif task_type == "generate_content":
                result = await self.generate_trend_content(
                    TrendOpportunity(**task["opportunity"]),
                    task["platform"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            
            if isinstance(result, list):
                return [r.model_dump() if hasattr(r, 'model_dump') else r for r in result]
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            logger.error(f"Trend hunter error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def analyze_trends(
        self,
        platform_data: Dict[str, List[str]],
        client_niche: str
    ) -> List[TrendingTopic]:
        """Analyze platform data and identify relevant trends"""
        trends = []
        
        for platform, topics in platform_data.items():
            for topic in topics[:5]:  # Limit to top 5 per platform
                # Use AI to analyze trend
                prompt = (
                    f"Analyze this trending topic for {client_niche}:\n"
                    f"Platform: {platform}\n"
                    f"Topic: {topic}\n\n"
                    f"Provide:\n"
                    f"1. Trend velocity (rising/peak/declining)\n"
                    f"2. Risk level (safe/moderate/risky)\n"
                    f"3. Content angle\n"
                    f"4. Audience alignment (0-1)\n"
                )
                
                analysis = await openai_service.generate_text(
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.6
                )
                
                # Calculate trend score
                trend_score = trend_processor.calculate_trend_score(
                    engagement_velocity=0.7,
                    share_rate=0.6
                )
                
                # Estimate lifespan
                lifespan = trend_processor.estimate_lifespan(
                    velocity="rising",
                    topic_type="general"
                )
                
                trend = TrendingTopic(
                    topic=topic,
                    platform=platform,
                    trend_score=trend_score,
                    velocity="rising",
                    estimated_lifespan=lifespan,
                    relevant_hashtags=[f"#{topic.replace(' ', '')}", "#trending"],
                    content_angle="Educational and entertaining",
                    risk_level="safe",
                    audience_alignment=0.75
                )
                
                trends.append(trend)
        
        return trends
    
    async def predict_virality(
        self,
        content_description: str,
        platform: str,
        target_audience: str
    ) -> ViralityPrediction:
        """Predict virality potential of content"""
        prompt = (
            f"Predict virality for this content:\n"
            f"Description: {content_description}\n"
            f"Platform: {platform}\n"
            f"Audience: {target_audience}\n\n"
            f"Provide:\n"
            f"1. Virality score (0-1)\n"
            f"2. 3 success factors\n"
            f"3. 2 risk factors\n"
            f"4. Best timing\n"
        )
        
        prediction_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.6
        )
        
        # Calculate virality score
        virality_score = trend_processor.predict_virality_score(
            engagement_rate=0.65,
            share_potential=0.7,
            timing_score=0.8
        )
        
        # Calculate platform fit
        platform_fit = trend_processor.calculate_platform_fit(
            content_type="video",
            platforms=["instagram", "tiktok", "facebook", "twitter"]
        )
        
        # Recommended timing
        recommended_time = (datetime.now() + timedelta(hours=2)).isoformat()
        
        return ViralityPrediction(
            content_description=content_description,
            virality_score=virality_score,
            predicted_reach_multiplier=2.5,
            key_success_factors=[
                "Strong hook in first 3 seconds",
                "Trending audio/music",
                "Clear call-to-action"
            ],
            recommended_timing=recommended_time,
            platform_fit=platform_fit,
            risk_factors=["Trend may fade quickly", "High competition"]
        )
    
    async def find_opportunities(
        self,
        trends: List[TrendingTopic],
        client_niche: str,
        brand_profile: Dict[str, str]
    ) -> List[TrendOpportunity]:
        """Find actionable trend opportunities"""
        opportunities = []
        
        niche_keywords = client_niche.lower().split()
        
        for trend in trends:
            # Calculate relevance
            trend_keywords = trend.topic.lower().split()
            relevance = trend_processor.calculate_relevance(
                trend_keywords, niche_keywords
            )
            
            if relevance < 0.3:
                continue  # Skip irrelevant trends
            
            # Generate content ideas
            prompt = (
                f"Generate 3 content ideas for:\n"
                f"Trend: {trend.topic}\n"
                f"Niche: {client_niche}\n"
                f"Brand tone: {brand_profile.get('tone', 'professional')}\n"
            )
            
            ideas_text = await openai_service.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.8
            )
            
            content_ideas = [
                i.strip() for i in ideas_text.split('\n')
                if i.strip() and len(i.strip()) > 10
            ][:3]
            
            # Determine urgency
            if trend.velocity == "peak":
                urgency = "act_now"
            elif trend.estimated_lifespan == "hours":
                urgency = "act_now"
            elif trend.estimated_lifespan == "days":
                urgency = "this_week"
            else:
                urgency = "next_week"
            
            # Estimate effort
            effort = trend_processor.estimate_effort(
                content_complexity="simple",
                resources_available=True
            )
            
            # Potential impact
            if trend.trend_score > 0.8 and relevance > 0.7:
                impact = "viral"
            elif trend.trend_score > 0.6:
                impact = "high"
            elif trend.trend_score > 0.4:
                impact = "medium"
            else:
                impact = "low"
            
            opportunity = TrendOpportunity(
                trend=trend,
                relevance_to_niche=relevance,
                content_ideas=content_ideas,
                urgency=urgency,
                effort_required=effort,
                potential_impact=impact
            )
            
            opportunities.append(opportunity)
        
        # Sort by potential impact
        impact_order = {"viral": 4, "high": 3, "medium": 2, "low": 1}
        opportunities.sort(
            key=lambda x: impact_order.get(x.potential_impact, 0),
            reverse=True
        )
        
        return opportunities[:5]  # Top 5 opportunities
    
    async def generate_trend_content(
        self,
        opportunity: TrendOpportunity,
        platform: str
    ) -> Dict[str, str]:
        """Generate specific content idea for trend"""
        prompt = (
            f"Create a specific content idea:\n"
            f"Trend: {opportunity.trend.topic}\n"
            f"Platform: {platform}\n"
            f"Urgency: {opportunity.urgency}\n"
            f"Ideas: {', '.join(opportunity.content_ideas)}\n\n"
            f"Provide:\n"
            f"1. Hook/title\n"
            f"2. Content outline\n"
            f"3. Call-to-action\n"
        )
        
        content = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.8
        )
        
        return {
            "trend": opportunity.trend.topic,
            "platform": platform,
            "content_idea": content.strip(),
            "urgency": opportunity.urgency,
            "potential_impact": opportunity.potential_impact
        }


# Global instance
trend_hunter_agent = TrendHunterAgent()
