"""
Engagement Agent
Handles user interactions and community management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.sentiment_processor import (
    sentiment_processor,
    CommentAnalysis
)

logger = logging.getLogger(__name__)


class EngagementResponse(BaseModel):
    """Response to user engagement"""
    response_text: str
    tone_used: str
    requires_human_review: bool
    escalation_reason: Optional[str] = None
    confidence: float
    suggested_alternatives: List[str]


class CrisisAssessment(BaseModel):
    """Crisis detection assessment"""
    is_crisis: bool
    severity: str  # "low" | "medium" | "high" | "critical"
    affected_comments: int
    recommended_action: str
    suggested_response: str


class EngagementAgent(BaseAgent):
    """
    Agent specialized in user engagement
    - Comment responses
    - DM handling
    - Sentiment analysis
    - Crisis detection
    """
    
    def __init__(self, agent_id: str = "engagement_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ENGAGEMENT,
            model="gpt-4o",
            tools=[
                "sentiment_analyzer",
                "toxicity_detector",
                "language_translator",
                "response_generator"
            ]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute engagement task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "respond_comment":
                result = await self.respond_to_comment(
                    comment=task["comment"],
                    platform=task.get("platform", "instagram"),
                    brand_voice=task.get("brand_voice", "friendly"),
                    context=task.get("context", {})
                )
            elif task_type == "handle_dm":
                result = await self.handle_dm(
                    message=task["message"],
                    platform=task["platform"],
                    conversation_history=task.get("conversation_history", [])
                )
            elif task_type == "analyze":
                result = await self._analyze_comment(task["comment"])
            elif task_type == "detect_crisis":
                result = await self.detect_crisis(task["comments"])
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            logger.error(f"Engagement execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def respond_to_comment(
        self,
        comment: str,
        platform: str,
        brand_voice: str,
        context: Dict[str, Any]
    ) -> EngagementResponse:
        """Generate contextual response to comment"""
        # Analyze comment first
        analysis = sentiment_processor.analyze_comment(comment)
        
        # Build prompt based on analysis
        prompt = self._build_response_prompt(
            comment, analysis, platform, brand_voice, context
        )
        
        # Generate response with GPT-4
        response_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        
        # Generate alternatives
        alt_prompt = f"{prompt}\n\nProvide 2 alternative responses (one line each):"
        alternatives_text = await openai_service.generate_text(
            prompt=alt_prompt,
            max_tokens=100,
            temperature=0.8
        )
        
        alternatives = [
            line.strip() for line in alternatives_text.split('\n')
            if line.strip() and len(line.strip()) > 10
        ][:2]
        
        response = EngagementResponse(
            response_text=response_text.strip(),
            tone_used=brand_voice,
            requires_human_review=analysis.requires_human,
            escalation_reason=self._get_escalation_reason(analysis),
            confidence=analysis.sentiment.confidence,
            suggested_alternatives=alternatives
        )
        return response.model_dump()
    
    async def handle_dm(
        self,
        message: str,
        platform: str,
        conversation_history: List[Dict[str, Any]]
    ) -> EngagementResponse:
        """Handle direct message"""
        analysis = sentiment_processor.analyze_comment(message)
        
        # Build context from history
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-5:]  # Last 5 messages
        ])
        
        prompt = (
            f"You are a {platform} customer service agent.\n"
            f"Conversation history:\n{history_text}\n\n"
            f"User message: {message}\n"
            f"Intent: {analysis.intent.intent}\n"
            f"Sentiment: {analysis.sentiment.label}\n\n"
            f"Provide a helpful, professional response:"
        )
        
        response_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.6
        )
        
        response = EngagementResponse(
            response_text=response_text.strip(),
            tone_used="professional",
            requires_human_review=analysis.urgency_score > 0.7,
            escalation_reason="High urgency DM" if analysis.urgency_score > 0.7 else None,
            confidence=0.8,
            suggested_alternatives=[]
        )
        return response.model_dump()
    
    async def detect_crisis(
        self,
        comments: List[str]
    ) -> CrisisAssessment:
        """Detect potential PR crisis"""
        if not comments:
            assessment = CrisisAssessment(
                is_crisis=False,
                severity="low",
                affected_comments=0,
                recommended_action="No action needed",
                suggested_response=""
            )
            return assessment.model_dump()
        
        # Analyze all comments
        analyses = [sentiment_processor.analyze_comment(c) for c in comments]
        
        # Calculate metrics
        negative_count = sum(
            1 for a in analyses if a.sentiment.label == "negative"
        )
        complaint_count = sum(
            1 for a in analyses if a.intent.intent == "complaint"
        )
        
        negative_ratio = negative_count / len(comments)
        
        # Determine crisis level
        is_crisis = negative_ratio > 0.3 or complaint_count > 5
        
        if negative_ratio > 0.6:
            severity = "critical"
        elif negative_ratio > 0.4:
            severity = "high"
        elif negative_ratio > 0.3:
            severity = "medium"
        else:
            severity = "low"
        
        # Generate response if crisis
        if is_crisis:
            prompt = (
                f"Crisis detected: {negative_count}/{len(comments)} negative comments.\n"
                f"Complaints: {complaint_count}\n\n"
                f"Generate a professional crisis response statement:"
            )
            
            suggested_response = await openai_service.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.5
            )
        else:
            suggested_response = ""
        
        assessment = CrisisAssessment(
            is_crisis=is_crisis,
            severity=severity,
            affected_comments=negative_count,
            recommended_action=self._get_crisis_action(severity),
            suggested_response=suggested_response.strip()
        )
        return assessment.model_dump()
    
    async def _analyze_comment(self, comment: str) -> Dict[str, Any]:
        """Analyze single comment"""
        analysis = sentiment_processor.analyze_comment(comment)
        return analysis.model_dump()
    
    def _build_response_prompt(
        self,
        comment: str,
        analysis: CommentAnalysis,
        platform: str,
        brand_voice: str,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for response generation"""
        tone_guide = {
            "friendly": "warm, approachable, and enthusiastic",
            "professional": "polite, formal, and respectful",
            "casual": "relaxed, conversational, and fun",
            "formal": "professional, courteous, and precise"
        }
        
        tone = tone_guide.get(brand_voice, "friendly")
        
        prompt = (
            f"You are responding to a {platform} comment.\n"
            f"Comment: {comment}\n"
            f"Sentiment: {analysis.sentiment.label}\n"
            f"Intent: {analysis.intent.intent}\n"
            f"Tone: {tone}\n\n"
            f"Generate a {tone} response (max 2 sentences):"
        )
        
        return prompt
    
    def _get_escalation_reason(self, analysis: CommentAnalysis) -> Optional[str]:
        """Get reason for human escalation"""
        if not analysis.requires_human:
            return None
        
        if analysis.urgency_score > 0.8:
            return "High urgency detected"
        if analysis.sentiment.score < -0.7:
            return "Very negative sentiment"
        if analysis.intent.intent == "complaint":
            return "Complaint detected"
        
        return "Manual review recommended"
    
    def _get_crisis_action(self, severity: str) -> str:
        """Get recommended action for crisis"""
        actions = {
            "critical": "Immediate executive notification and public statement required",
            "high": "Notify management and prepare official response",
            "medium": "Monitor closely and prepare response template",
            "low": "Continue monitoring, no immediate action needed"
        }
        return actions.get(severity, "Monitor situation")


# Global instance
engagement_agent = EngagementAgent()
