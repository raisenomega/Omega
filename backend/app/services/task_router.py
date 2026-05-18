"""
Task Router Service
Pure workflow orchestration and task routing logic
"""
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import uuid


class AgentTask(BaseModel):
    """Individual task for an agent"""
    task_id: str
    workflow_id: str | None
    task_type: str  # "generate_content" | "validate_brand" | "analyze_metrics" | etc.
    assigned_agent: str  # "content_creator" | "brand_voice" | "analytics" | etc.
    priority: str  # "low" | "normal" | "high" | "critical"
    payload: dict[str, str | int | float | List | Dict]
    status: str  # "queued" | "processing" | "completed" | "failed"
    created_at: str
    started_at: str | None
    completed_at: str | None
    result: dict[str, str | int | float | List] | None
    error: str | None


class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    step_id: str
    agent: str
    action: str
    depends_on: List[str]  # step_ids that must complete before
    parallel_with: List[str]  # step_ids that can run simultaneously


class WorkflowExecution(BaseModel):
    """Running workflow instance"""
    workflow_id: str
    workflow_name: str
    client_id: str
    status: str  # "running" | "completed" | "failed" | "paused"
    steps: List[WorkflowStep]
    completed_steps: List[str]
    current_step: str | None
    started_at: str
    estimated_completion: str | None
    results: dict[str, Dict]  # step_id -> result


class OrchestratorState(BaseModel):
    """System-wide orchestrator state"""
    active_workflows: int
    queued_tasks: int
    agents_online: int
    agents_status: dict[str, str]
    system_load: float  # 0.0 to 1.0
    last_health_check: str


def generate_task_id() -> str:
    """
    Generate unique task ID

    Returns:
        Unique task identifier
    """
    return f"task_{uuid.uuid4().hex[:12]}"


def generate_workflow_id() -> str:
    """
    Generate unique workflow ID

    Returns:
        Unique workflow identifier
    """
    return f"workflow_{uuid.uuid4().hex[:12]}"


def get_next_available_step(workflow: WorkflowExecution) -> WorkflowStep | None:
    """
    Get next step that can be executed

    Args:
        workflow: Workflow execution instance

    Returns:
        Next available step or None
    """
    for step in workflow.steps:
        # Skip if already completed
        if step.step_id in workflow.completed_steps:
            continue

        # Check if dependencies are met
        dependencies_met = all(
            dep_id in workflow.completed_steps
            for dep_id in step.depends_on
        )

        if dependencies_met:
            return step

    return None


def calculate_system_load(active_workflows: int, queued_tasks: int) -> float:
    """
    Calculate system load (0.0 to 1.0)

    Args:
        active_workflows: Number of active workflows
        queued_tasks: Number of queued tasks

    Returns:
        System load percentage
    """
    # Simple load calculation (in production, consider CPU, memory, etc.)
    max_workflows = 50
    max_tasks = 200

    workflow_load = min(active_workflows / max_workflows, 1.0)
    task_load = min(queued_tasks / max_tasks, 1.0)

    # Weighted average
    return (workflow_load * 0.6 + task_load * 0.4)


def route_task_to_agent(task_type: str) -> str:
    """
    Route task to appropriate agent

    Args:
        task_type: Type of task

    Returns:
        Agent name
    """
    task_routing = {
        "generate_content": "content_creator",
        "validate_brand_voice": "brand_voice",
        "analyze_metrics": "analytics",
        "respond_comments": "engagement",
        "assess_crisis": "crisis_manager",
        "analyze_competitors": "competitive_intel",
        "hunt_trends": "trend_hunter",
        "generate_report": "report_generator",
        "optimize_growth": "growth_hacker",
        "create_strategy": "strategy",
        "monitor_health": "monitor",
        "write_video_script": "video_production",
        "schedule_post": "scheduling",
        "design_experiment": "ab_testing"
    }

    return task_routing.get(task_type, "content_creator")


def get_workflow_progress(workflow: WorkflowExecution) -> float:
    """
    Calculate workflow progress percentage

    Args:
        workflow: Workflow execution instance

    Returns:
        Progress percentage (0.0 to 1.0)
    """
    if not workflow.steps:
        return 0.0

    completed_count = len(workflow.completed_steps)
    total_steps = len(workflow.steps)

    return completed_count / total_steps


def estimate_workflow_completion(workflow: WorkflowExecution) -> str:
    """
    Estimate workflow completion time

    Args:
        workflow: Workflow execution instance

    Returns:
        ISO datetime string
    """
    # Average time per step (simplified)
    avg_step_time_seconds = 30

    remaining_steps = len(workflow.steps) - len(workflow.completed_steps)
    estimated_seconds = remaining_steps * avg_step_time_seconds

    started_dt = datetime.fromisoformat(workflow.started_at)
    estimated_dt = datetime.fromtimestamp(
        started_dt.timestamp() + estimated_seconds
    )

    return estimated_dt.isoformat()


def prioritize_tasks(tasks: List[AgentTask]) -> List[AgentTask]:
    """
    Sort tasks by priority

    Args:
        tasks: List of tasks

    Returns:
        Sorted tasks (critical first)
    """
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}

    return sorted(
        tasks,
        key=lambda t: priority_order.get(t.priority, 2)
    )
