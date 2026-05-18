"""
Crisis Manager Agent
Handles crisis detection, response and recovery
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.claude_service import claude_service
from app.services.crisis_detector import (
    crisis_detector,
    CrisisSignals,
    CrisisImpactAssessment,
    CrisisLevel,
    RecoveryStep
)

logger = logging.getLogger(__name__)


class CrisisManagerAgent(BaseAgent):
    """
    Agent specialized in crisis management
    - Crisis assessment
    - Response strategy
    - Official statements
    - Recovery planning
    """
    
    def __init__(self, agent_id: str = "crisis_manager_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CRISIS_MANAGER,
            model="claude-opus-4",
            tools=[
                "crisis_assessor",
                "response_strategist",
                "statement_drafter",
                "recovery_planner"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute crisis management task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "assess":
                result = await self.assess_crisis(
                    CrisisSignals(**task["signals"])
                )
            elif task_type == "response_strategy":
                result = await self.generate_response_strategy(
                    CrisisImpactAssessment(**task["assessment"]),
                    task["brand_profile"]
                )
            elif task_type == "draft_statement":
                result = await self.draft_official_statement(
                    CrisisImpactAssessment(**task["assessment"]),
                    task["brand_voice"],
                    task["brand_name"]
                )
            elif task_type == "recovery_plan":
                result = await self.create_recovery_plan(
                    CrisisImpactAssessment(**task["assessment"])
                )
            elif task_type == "immediate_actions":
                result = await self.recommend_immediate_actions(
                    CrisisLevel(**task["crisis_level"])
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            
            if isinstance(result, list):
                return [r.model_dump() if hasattr(r, 'model_dump') else r for r in result]
            return result.model_dump() if hasattr(result, 'model_dump') else result
            
        except Exception as e:
            logger.error(f"Crisis manager error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def assess_crisis(
        self,
        signals: CrisisSignals
    ) -> CrisisImpactAssessment:
        """Assess crisis impact and severity"""
        # Calculate crisis score
        score = crisis_detector.calculate_crisis_score(signals)
        level_str = crisis_detector.classify_crisis_level(score)
        
        # Identify triggers
        triggers = []
        if signals.negative_comment_percentage > 0.5:
            triggers.append("High negative sentiment")
        if signals.complaint_velocity > 5:
            triggers.append("Complaint surge")
        if signals.media_involvement:
            triggers.append("Media coverage")
        if signals.influencer_involvement:
            triggers.append("Influencer involvement")
        
        crisis_level = CrisisLevel(
            level=level_str,
            score=score,
            triggers=triggers
        )
        
        # Use Claude for deep analysis
        prompt = (
            f"Crisis Assessment:\n"
            f"Level: {level_str} (score: {score:.2f})\n"
            f"Platform: {signals.platform}\n"
            f"Triggers: {', '.join(triggers)}\n"
            f"Negative sentiment: {signals.negative_comment_percentage:.1%}\n"
            f"Reach: {signals.reach_of_negative_content}\n\n"
            f"Assess:\n"
            f"1. Reputation damage (minimal/moderate/severe/critical)\n"
            f"2. Affected platforms\n"
            f"3. Recovery time estimate\n"
        )
        
        analysis = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.5
        )
        
        # Determine damage level
        if score > 0.8:
            damage = "critical"
        elif score > 0.6:
            damage = "severe"
        elif score > 0.4:
            damage = "moderate"
        else:
            damage = "minimal"
        
        recovery_time = crisis_detector.estimate_recovery_time(damage, level_str)
        brand_impact = crisis_detector.estimate_brand_equity_impact(
            score, signals.reach_of_negative_content
        )
        
        return CrisisImpactAssessment(
            crisis_level=crisis_level,
            estimated_reputation_damage=damage,
            affected_platforms=[signals.platform],
            estimated_recovery_time=recovery_time,
            brand_equity_impact=brand_impact,
            requires_immediate_action=crisis_detector.requires_immediate_action(level_str)
        )
    
    async def generate_response_strategy(
        self,
        assessment: CrisisImpactAssessment,
        brand_profile: Dict[str, str]
    ) -> Dict[str, str | List[str]]:
        """Generate crisis response strategy"""
        prompt = (
            f"Crisis Response Strategy:\n"
            f"Level: {assessment.crisis_level.level}\n"
            f"Damage: {assessment.estimated_reputation_damage}\n"
            f"Brand: {brand_profile.get('name', 'Client')}\n"
            f"Tone: {brand_profile.get('tone', 'professional')}\n\n"
            f"Create response strategy:\n"
            f"1. Immediate actions (next 60 min)\n"
            f"2. Communication approach\n"
            f"3. Stakeholder priorities\n"
            f"4. Key messages\n"
        )
        
        strategy = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.6
        )
        
        return {
            "strategy": strategy,
            "priority": assessment.crisis_level.level,
            "immediate_action_required": assessment.requires_immediate_action
        }
    
    async def draft_official_statement(
        self,
        assessment: CrisisImpactAssessment,
        brand_voice: str,
        brand_name: str
    ) -> str:
        """Draft official crisis statement"""
        prompt = (
            f"Draft official statement for {brand_name}:\n"
            f"Crisis level: {assessment.crisis_level.level}\n"
            f"Triggers: {', '.join(assessment.crisis_level.triggers)}\n"
            f"Brand voice: {brand_voice}\n\n"
            f"Requirements:\n"
            f"- Acknowledge the issue\n"
            f"- Show empathy\n"
            f"- Outline actions being taken\n"
            f"- Maintain brand voice\n"
            f"- Professional and sincere\n"
        )
        
        statement = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )
        
        return statement.strip()
    
    async def create_recovery_plan(
        self,
        assessment: CrisisImpactAssessment
    ) -> List[RecoveryStep]:
        """Create step-by-step recovery plan"""
        steps = [
            RecoveryStep(
                step_number=1,
                action="Issue official statement",
                responsible="both",
                deadline="immediate",
                success_metric="Statement published and acknowledged"
            ),
            RecoveryStep(
                step_number=2,
                action="Monitor social sentiment",
                responsible="agency",
                deadline="24h",
                success_metric="Sentiment tracking dashboard active"
            ),
            RecoveryStep(
                step_number=3,
                action="Respond to key stakeholders",
                responsible="client",
                deadline="24h",
                success_metric="All priority stakeholders contacted"
            ),
            RecoveryStep(
                step_number=4,
                action="Implement corrective measures",
                responsible="client",
                deadline="48h",
                success_metric="Action plan communicated publicly"
            ),
            RecoveryStep(
                step_number=5,
                action="Launch reputation rebuild campaign",
                responsible="both",
                deadline="1week",
                success_metric="Positive sentiment increase by 20%"
            )
        ]
        
        return steps
    
    async def recommend_immediate_actions(
        self,
        crisis_level: CrisisLevel
    ) -> List[str]:
        """Recommend actions for next 60 minutes"""
        if crisis_level.level == "emergency":
            return [
                "Pause all scheduled content immediately",
                "Alert client leadership team",
                "Draft crisis statement (15 min deadline)",
                "Activate crisis response team",
                "Monitor all platforms in real-time"
            ]
        elif crisis_level.level == "crisis":
            return [
                "Pause scheduled content for 24h",
                "Notify client immediately",
                "Prepare holding statement",
                "Increase monitoring frequency",
                "Assess legal/PR consultation needs"
            ]
        elif crisis_level.level == "alert":
            return [
                "Review upcoming content",
                "Inform client of situation",
                "Prepare response templates",
                "Monitor sentiment closely"
            ]
        else:
            return [
                "Continue monitoring",
                "Document incident",
                "Brief team on situation"
            ]


# Global instance
crisis_manager_agent = CrisisManagerAgent()
