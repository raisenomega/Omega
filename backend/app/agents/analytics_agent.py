"""
Analytics Agent
Processes metrics and generates insights
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.analytics_processor import analytics_processor

logger = logging.getLogger(__name__)


class AnalyticsAgent(BaseAgent):
    """
    Agent specialized in data analysis and insights
    - Metrics processing
    - Pattern detection
    - Performance forecasting
    - Anomaly detection
    - Dashboard data generation
    """
    
    def __init__(self, agent_id: str = "analytics_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYTICS,
            model="gpt-4",
            tools=[
                "data_processor",
                "stats_analyzer",
                "anomaly_detector",
                "forecaster",
                "insight_generator"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analytics task
        
        Args:
            task: Task parameters
                - type: "analyze" | "patterns" | "insights" | "forecast" | "dashboard"
                - data: Metrics data
                
        Returns:
            Analysis results
        """
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "analyze":
                result = await self._analyze_metrics(task)
            elif task_type == "patterns":
                result = await self._detect_patterns(task)
            elif task_type == "insights":
                result = await self._generate_insights(task)
            elif task_type == "forecast":
                result = await self._forecast_performance(task)
            elif task_type == "dashboard":
                result = await self._get_dashboard_data(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Store in memory
            await self.store_memory(f"last_{task_type}", result)
            
            self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            logger.error(f"Analytics execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def _analyze_metrics(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze metrics data"""
        data = task.get("data", {})
        
        # Extract metrics
        likes = data.get("likes", 0)
        comments = data.get("comments", 0)
        shares = data.get("shares", 0)
        followers = data.get("followers", 1000)
        impressions = data.get("impressions", 0)
        
        # Calculate engagement rate
        engagement_rate = analytics_processor.calculate_engagement_rate(
            likes, comments, shares, followers
        )
        
        # Calculate reach percentage
        reach_pct = (impressions / followers * 100) if followers > 0 else 0
        
        # Generate AI insights
        prompt = (
            f"Analyze these social media metrics:\n"
            f"- Engagement Rate: {engagement_rate}%\n"
            f"- Likes: {likes}\n"
            f"- Comments: {comments}\n"
            f"- Shares: {shares}\n"
            f"- Reach: {reach_pct:.1f}%\n\n"
            f"Provide 3 actionable insights to improve performance."
        )
        
        ai_insights = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        
        return {
            "metrics": {
                "engagement_rate": engagement_rate,
                "reach_percentage": round(reach_pct, 2),
                "total_interactions": likes + comments + shares,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "impressions": impressions,
                "followers": followers
            },
            "ai_insights": ai_insights,
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def _detect_patterns(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect patterns in historical data"""
        historical_data = task.get("historical_data", [])
        
        if not historical_data:
            return {"patterns": [], "message": "No data provided"}
        
        # Extract values
        values = [item.get("value", 0) for item in historical_data]
        
        # Calculate moving average
        moving_avg = analytics_processor.calculate_moving_average(
            values, window_size=7
        )
        
        # Detect anomalies
        anomalies = analytics_processor.detect_anomalies(values)
        
        # Calculate trend
        if len(values) >= 2:
            growth_rate = analytics_processor.calculate_growth_rate(
                values[-1], values[0]
            )
        else:
            growth_rate = 0.0
        
        # Generate AI pattern analysis
        prompt = (
            f"Analyze this time series data:\n"
            f"- Data points: {len(values)}\n"
            f"- Overall growth: {growth_rate}%\n"
            f"- Anomalies detected: {len(anomalies)}\n"
            f"- Latest value: {values[-1] if values else 0}\n\n"
            f"Identify key patterns and trends."
        )
        
        ai_analysis = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.6
        )
        
        return {
            "patterns": {
                "moving_average": moving_avg[-7:] if len(moving_avg) >= 7 else moving_avg,
                "anomalies": anomalies,
                "growth_rate": growth_rate,
                "trend": "upward" if growth_rate > 0 else "downward"
            },
            "ai_analysis": ai_analysis,
            "data_points": len(values)
        }
    
    async def _generate_insights(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable insights"""
        metrics = task.get("metrics", {})
        
        # Build comprehensive prompt
        prompt = self._build_insights_prompt(metrics)
        
        # Generate insights with GPT-4
        insights_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )
        
        return {
            "insights": insights_text,
            "metrics_analyzed": list(metrics.keys()),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _forecast_performance(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forecast future performance"""
        historical = task.get("historical_data", [])
        days_ahead = task.get("days_ahead", 7)
        
        if len(historical) < 3:
            return {
                "forecast": [],
                "message": "Insufficient data for forecasting"
            }
        
        # Simple linear forecast
        values = [item.get("value", 0) for item in historical]
        
        # Calculate average growth
        if len(values) >= 2:
            growth_rate = analytics_processor.calculate_growth_rate(
                values[-1], values[0]
            ) / len(values)
        else:
            growth_rate = 0
        
        # Generate forecast
        forecast = []
        last_value = values[-1]
        
        for day in range(1, days_ahead + 1):
            predicted_value = last_value * (1 + growth_rate / 100) ** day
            forecast.append({
                "day": day,
                "predicted_value": round(predicted_value, 2)
            })
        
        return {
            "forecast": forecast,
            "growth_rate": growth_rate,
            "confidence": "medium",
            "days_ahead": days_ahead
        }
    
    async def _get_dashboard_data(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        filters = task.get("filters", {})
        
        # Generate sample dashboard data
        # In production, this would query actual database
        dashboard = {
            "overview": {
                "total_posts": 45,
                "total_followers": 12500,
                "avg_engagement_rate": 4.2,
                "total_reach": 85000
            },
            "recent_performance": {
                "last_7_days": {
                    "posts": 7,
                    "new_followers": 250,
                    "engagement_rate": 4.5
                },
                "last_30_days": {
                    "posts": 28,
                    "new_followers": 980,
                    "engagement_rate": 4.1
                }
            },
            "top_performing_posts": [],
            "generated_at": datetime.now().isoformat()
        }
        
        return dashboard
    
    def _build_insights_prompt(self, metrics: Dict[str, Any]) -> str:
        """Build prompt for insights generation"""
        prompt_parts = [
            "Generate actionable insights from these metrics:",
            ""
        ]
        
        for key, value in metrics.items():
            prompt_parts.append(f"- {key}: {value}")
        
        prompt_parts.extend([
            "",
            "Provide:",
            "1. Key observations",
            "2. Areas of concern",
            "3. Opportunities for improvement",
            "4. Specific action items"
        ])
        
        return "\n".join(prompt_parts)


# Global instance
analytics_agent = AnalyticsAgent()
