"""
Client Context Entity
Shared memory and learning context for each client
Filosofía: No velocity, only precision 🐢💎
"""
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass
class ClientContext:
    """
    Client Context Entity

    Represents shared memory and learning data for a client,
    accessible by all agents for context-aware operations.
    """
    # Identity
    id: Optional[str] = None
    client_id: str = ""

    # Brand Identity
    niche: Optional[str] = None
    tone: Optional[str] = None
    brand_voice: dict[str, Any] = field(default_factory=dict)
    target_audience: Optional[str] = None

    # Competitive Intelligence
    competitors: list[dict[str, Any]] = field(default_factory=list)

    # Performance Data
    best_performing_content: list[dict[str, Any]] = field(default_factory=list)
    posting_patterns: dict[str, Any] = field(default_factory=dict)

    # Analytics Insights
    avg_engagement_rate: Optional[float] = None
    peak_posting_hours: list[str] = field(default_factory=list)
    top_hashtags: list[str] = field(default_factory=list)
    audience_demographics: dict[str, Any] = field(default_factory=dict)

    # Content Preferences
    content_themes: list[str] = field(default_factory=list)
    avoided_topics: list[str] = field(default_factory=list)
    preferred_formats: list[str] = field(default_factory=list)

    # Metadata
    last_updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_brand_voice(self, agent_id: str, voice_data: dict[str, Any]) -> None:
        """Update brand voice from agent learning"""
        self.brand_voice.update(voice_data)
        self.last_updated_by = agent_id

    def add_competitor(self, competitor_data: dict[str, Any]) -> None:
        """Add competitor intelligence"""
        if competitor_data not in self.competitors:
            self.competitors.append(competitor_data)

    def add_best_performing_content(self, content: dict[str, Any]) -> None:
        """Track high-performing content"""
        self.best_performing_content.append(content)
        # Keep only top 20
        if len(self.best_performing_content) > 20:
            self.best_performing_content = sorted(
                self.best_performing_content,
                key=lambda x: x.get("engagement_rate", 0),
                reverse=True
            )[:20]

    def update_posting_patterns(self, patterns: dict[str, Any]) -> None:
        """Update optimal posting patterns"""
        self.posting_patterns.update(patterns)

    def update_analytics(
        self,
        engagement_rate: Optional[float] = None,
        peak_hours: Optional[list[str]] = None,
        hashtags: Optional[list[str]] = None,
        demographics: Optional[dict[str, Any]] = None
    ) -> None:
        """Update analytics insights"""
        if engagement_rate is not None:
            self.avg_engagement_rate = engagement_rate
        if peak_hours:
            self.peak_posting_hours = peak_hours
        if hashtags:
            self.top_hashtags = hashtags[:30]  # Keep top 30
        if demographics:
            self.audience_demographics.update(demographics)

    def has_context(self) -> bool:
        """Check if context has been initialized"""
        return bool(self.niche or self.brand_voice or self.best_performing_content)
