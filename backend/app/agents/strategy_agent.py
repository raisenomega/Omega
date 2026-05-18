"""
Strategy Agent
Creates content calendars and optimizes posting strategy
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.claude_service import claude_service

logger = logging.getLogger(__name__)


class StrategyAgent(BaseAgent):
    """
    Agent specialized in content strategy and planning
    - Content calendar creation
    - Posting time optimization
    - Content mix balancing
    - Cross-platform strategy
    """
    
    def __init__(self, agent_id: str = "strategy_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.STRATEGY,
            model="claude-opus-4",
            tools=[
                "calendar_optimizer",
                "timing_analyzer",
                "content_mixer",
                "roi_calculator"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute strategy task
        
        Args:
            task: Task parameters
                - type: "calendar" | "timing" | "mix" | "analysis"
                - context: Business context
                - goals: Strategic goals
                
        Returns:
            Strategic recommendations
        """
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "calendar":
                result = await self._create_calendar(task)
            elif task_type == "timing":
                result = await self._optimize_timing(task)
            elif task_type == "mix":
                result = await self._balance_content_mix(task)
            elif task_type == "analysis":
                result = await self._analyze_strategy(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Store in memory
            await self.store_memory(f"last_{task_type}", result)
            
            self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            logger.error(f"Strategy execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def _create_calendar(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create content calendar"""
        duration_days = task.get("duration_days", 30)
        platforms = task.get("platforms", ["instagram"])
        goals = task.get("goals", [])
        
        context = {
            "duration": f"{duration_days} days",
            "platforms": ", ".join(platforms),
            "current_date": datetime.now().isoformat()
        }
        
        strategy = await claude_service.analyze_strategy(
            context=context,
            goals=goals
        )
        
        # Generate calendar structure
        calendar = self._generate_calendar_structure(
            duration_days,
            platforms
        )
        
        return {
            "calendar": calendar,
            "strategy": strategy,
            "duration_days": duration_days,
            "platforms": platforms
        }
    
    async def _optimize_timing(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize posting times"""
        platform = task.get("platform", "instagram")
        timezone = task.get("timezone", "UTC")
        audience_data = task.get("audience_data", {})
        
        prompt = (
            f"Analyze optimal posting times for {platform}.\n"
            f"Timezone: {timezone}\n"
            f"Audience data: {audience_data}\n\n"
            f"Provide:\n"
            f"1. Best times to post (specific hours)\n"
            f"2. Days with highest engagement\n"
            f"3. Times to avoid\n"
            f"4. Reasoning for each recommendation"
        )
        
        analysis = await claude_service.generate_text(
            prompt=prompt,
            temperature=0.3
        )
        
        return {
            "platform": platform,
            "timezone": timezone,
            "recommendations": analysis,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _balance_content_mix(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Balance content types"""
        current_mix = task.get("current_mix", {})
        goals = task.get("goals", [])
        industry = task.get("industry", "general")
        
        prompt = (
            f"Optimize content mix for {industry} industry.\n\n"
            f"Current mix:\n"
        )
        
        for content_type, percentage in current_mix.items():
            prompt += f"- {content_type}: {percentage}%\n"
        
        prompt += f"\nGoals: {', '.join(goals)}\n\n"
        prompt += (
            "Recommend optimal content mix with percentages for:\n"
            "- Educational content\n"
            "- Entertainment\n"
            "- Promotional\n"
            "- User-generated content\n"
            "- Behind-the-scenes\n\n"
            "Explain reasoning for each."
        )
        
        recommendations = await claude_service.generate_text(
            prompt=prompt,
            temperature=0.4
        )
        
        return {
            "current_mix": current_mix,
            "recommended_mix": recommendations,
            "industry": industry
        }
    
    async def _analyze_strategy(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive strategy analysis"""
        context = task.get("context", {})
        goals = task.get("goals", [])
        constraints = task.get("constraints", {})
        
        strategy = await claude_service.analyze_strategy(
            context=context,
            goals=goals,
            constraints=constraints
        )
        
        return {
            "strategy": strategy,
            "context": context,
            "goals": goals,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_calendar_structure(
        self,
        duration_days: int,
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate basic calendar structure"""
        calendar = []
        start_date = datetime.now()
        
        for day in range(duration_days):
            date = start_date + timedelta(days=day)
            
            for platform in platforms:
                calendar.append({
                    "date": date.isoformat(),
                    "platform": platform,
                    "slots": [],  # To be filled by content
                    "status": "planned"
                })
        
        return calendar


# Global instance
strategy_agent = StrategyAgent()
