"""
Agent Mapper
Maps database rows to domain entities
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
from datetime import datetime

from app.domain.agents.entities import Agent, AgentExecution, AgentLog


def map_agent_to_entity(row: dict) -> Agent:
    """Map database row to Agent entity"""
    return Agent(
        id=row.get("id"),
        agent_id=row.get("agent_id", ""),
        name=row.get("name", ""),
        description=row.get("description"),
        department=row.get("department", ""),
        category=row.get("category"),
        status=row.get("status", "active"),
        version=row.get("version", "1.0.0"),
        capabilities=row.get("capabilities", []),
        input_schema=row.get("input_schema", {}),
        output_schema=row.get("output_schema", {}),
        config=row.get("config", {}),
        max_execution_time_seconds=row.get("max_execution_time_seconds", 300),
        retry_policy=row.get("retry_policy", {}),
        total_executions=row.get("total_executions", 0),
        successful_executions=row.get("successful_executions", 0),
        failed_executions=row.get("failed_executions", 0),
        avg_execution_time_ms=float(row.get("avg_execution_time_ms", 0)),
        last_executed_at=parse_datetime(row.get("last_executed_at")),
        is_active=row.get("is_active", True),
        created_at=parse_datetime(row.get("created_at")),
        updated_at=parse_datetime(row.get("updated_at")),
    )


def map_execution_to_entity(row: dict) -> AgentExecution:
    """Map database row to AgentExecution entity"""
    return AgentExecution(
        id=row.get("id"),
        agent_id=row.get("agent_id", ""),
        client_id=row.get("client_id"),
        user_id=row.get("user_id"),
        triggered_by=row.get("triggered_by", "manual"),
        input_data=row.get("input_data", {}),
        output_data=row.get("output_data", {}),
        error_message=row.get("error_message"),
        status=row.get("status", "pending"),
        started_at=parse_datetime(row.get("started_at")),
        completed_at=parse_datetime(row.get("completed_at")),
        execution_time_ms=row.get("execution_time_ms"),
        metadata=row.get("metadata", {}),
        is_active=row.get("is_active", True),
        created_at=parse_datetime(row.get("created_at")),
    )


def map_log_to_entity(row: dict) -> AgentLog:
    """Map database row to AgentLog entity"""
    return AgentLog(
        id=row.get("id"),
        execution_id=row.get("execution_id", ""),
        agent_id=row.get("agent_id", ""),
        level=row.get("level", "info"),
        message=row.get("message", ""),
        details=row.get("details", {}),
        logged_at=parse_datetime(row.get("logged_at")),
        created_at=parse_datetime(row.get("created_at")),
    )


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string"""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
