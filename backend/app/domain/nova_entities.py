"""
Nova Entities — Pydantic v2 models for NOVA context system.
DDD: Domain layer. Data shapes only — zero business logic.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NovaFullContext(BaseModel):
    """
    Maps the nova_full_context VIEW exactly.
    All IDs are str. [R-UUID-001]
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    # Identity (from clients table)
    client_id: str
    client_name: str
    nova_tier: str                          # sistema_only | nova_dedicated | company
    company_agents: list[str] = []
    onboarding_active: bool = False

    # Brand Identity (from client_context)
    niche: Optional[str] = None
    tone: Optional[str] = None
    business_what: Optional[str] = None
    business_to_whom: Optional[str] = None
    business_diff: Optional[str] = None
    business_geo: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: dict[str, str] = {}
    brand_file: dict[str, str] = {}

    # Goals & History
    goal_this_month: Optional[str] = None
    goal_this_quarter: Optional[str] = None
    goal_priority_now: Optional[str] = None
    what_worked: Optional[str] = None
    what_failed: Optional[str] = None

    # NOVA Intelligence
    nova_learnings: list[dict[str, str]] = []
    nova_can_publish: list[str] = []
    custom_instructions: Optional[str] = None

    # Content Strategy
    competitors: list[str] = []
    content_themes: list[str] = []
    posting_patterns: dict[str, str] = {}
    avg_engagement_rate: Optional[float] = None
    top_hashtags: list[str] = []
    avoided_topics: list[str] = []
    preferred_formats: list[str] = []
    onboarding_complete: bool = False


class NovaContextResponse(BaseModel):
    """Response shape for GET /nova/context/{client_id}"""
    model_config = ConfigDict(str_strip_whitespace=True)

    client_id: str
    client_name: str
    nova_tier: str
    system_prompt: str
    context_raw: NovaFullContext


class UpdateContextRequest(BaseModel):
    """Body for POST /nova/context/{client_id} [R-BODY-001]"""
    model_config = ConfigDict(str_strip_whitespace=True)

    niche: Optional[str] = None
    tone: Optional[str] = None
    business_what: Optional[str] = None
    business_to_whom: Optional[str] = None
    business_diff: Optional[str] = None
    business_geo: Optional[str] = None
    target_audience: Optional[str] = None
    goal_this_month: Optional[str] = None
    goal_this_quarter: Optional[str] = None
    goal_priority_now: Optional[str] = None
    what_worked: Optional[str] = None
    what_failed: Optional[str] = None
    custom_instructions: Optional[str] = None


class UpdateLearningRequest(BaseModel):
    """Body for PATCH /nova/context/{client_id}/learning [R-BODY-001]"""
    model_config = ConfigDict(str_strip_whitespace=True)

    learning_key: str
    learning_value: str
