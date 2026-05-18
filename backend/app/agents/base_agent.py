"""
Base Agent Framework
Foundation for all AI agents in the system
"""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent role types"""
    CONTENT_CREATOR = "content_creator"
    STRATEGY = "strategy"
    ANALYTICS = "analytics"
    ENGAGEMENT = "engagement"
    MONITOR = "monitor"
    BRAND_VOICE = "brand_voice"
    COMPETITIVE = "competitive"
    TREND_HUNTER = "trend_hunter"
    COMPETITIVE_INTEL = "competitive_intel"
    CRISIS_MANAGER = "crisis_manager"
    GROWTH_HACKER = "growth_hacker"
    REPORT_GENERATOR = "report_generator"
    VIDEO_PRODUCTION = "video_production"
    SCHEDULING = "scheduling"
    AB_TESTING = "ab_testing"
    ORCHESTRATOR = "orchestrator"


class AgentState(str, Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    PAUSED = "paused"


class BaseAgent(ABC):
    """
    Base class for all AI agents
    Implements common functionality and interface
    """
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        model: str,
        tools: Optional[List[str]] = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.model = model
        self.tools = tools or []
        self.state = AgentState.IDLE
        self.memory: Dict[str, Any] = {}
        
        logger.info(
            f"Initialized agent: {agent_id} "
            f"(role={role}, model={model})"
        )
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task
        Must be implemented by subclasses
        """
        pass
    
    async def plan(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Plan how to execute a task
        Returns list of steps
        """
        logger.info(f"Agent {self.agent_id} planning task")
        return [{"action": "execute", "params": task}]
    
    async def store_memory(self, key: str, value: Any) -> None:
        """Store information in agent memory"""
        self.memory[key] = value
        logger.debug(f"Agent {self.agent_id} stored memory: {key}")
    
    async def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent memory"""
        return self.memory.get(key)
    
    def set_state(self, state: AgentState) -> None:
        """Update agent state"""
        old_state = self.state
        self.state = state
        logger.info(
            f"Agent {self.agent_id} state: "
            f"{old_state} -> {state}"
        )
    
    async def communicate(
        self,
        target_agent_id: str,
        message: Dict[str, Any]
    ) -> None:
        """
        Send message to another agent
        To be implemented with message bus
        """
        logger.info(
            f"Agent {self.agent_id} sending message "
            f"to {target_agent_id}"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "model": self.model,
            "state": self.state,
            "tools": self.tools,
            "memory_size": len(self.memory)
        }
