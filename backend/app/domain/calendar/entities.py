"""
Calendar Domain Entities
Business entities for scheduled posts
Filosofía: No velocity, only precision 🐢💎
"""
from datetime import date, time, datetime
from typing import Optional
from dataclasses import dataclass

from .types import Status


@dataclass
class ScheduledPost:
    """
    Scheduled Post Entity

    Represents a social media post scheduled for future publication.
    Contains business logic for validation and state transitions.
    """
    # Identity
    id: Optional[str] = None

    # References
    client_id: str = ""
    account_id: str = ""
    content_lab_id: Optional[str] = None

    # Content
    content_type: str = "post"
    text_content: str = ""
    image_url: Optional[str] = None
    hashtags: list[str] = None

    # Scheduling
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    timezone: str = "America/Puerto_Rico"
    status: Status = "draft"

    # Agent tracking
    agent_assigned: str = "manual"

    # Metadata
    is_active: bool = True
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.hashtags is None:
            self.hashtags = []

    def is_scheduled(self) -> bool:
        """Check if post is in scheduled state"""
        return self.status == "scheduled"

    def is_published(self) -> bool:
        """Check if post has been published"""
        return self.status == "published"

    def can_be_edited(self) -> bool:
        """Check if post can be edited"""
        return self.status in ["draft", "scheduled", "failed"]

    def can_be_deleted(self) -> bool:
        """Check if post can be deleted"""
        return self.status != "publishing"

    def mark_as_scheduled(self) -> None:
        """Transition to scheduled status"""
        if self.status != "draft":
            raise ValueError(f"Cannot schedule post in {self.status} status")
        self.status = "scheduled"

    def mark_as_publishing(self) -> None:
        """Transition to publishing status"""
        if self.status != "scheduled":
            raise ValueError(f"Cannot publish post in {self.status} status")
        self.status = "publishing"

    def mark_as_published(self) -> None:
        """Transition to published status"""
        if self.status != "publishing":
            raise ValueError(f"Cannot mark as published from {self.status} status")
        self.status = "published"
        self.published_at = datetime.utcnow()

    def mark_as_failed(self, error: str) -> None:
        """Transition to failed status"""
        self.status = "failed"
        self.error_message = error

    def soft_delete(self) -> None:
        """Soft delete post (set is_active=False)"""
        if not self.can_be_deleted():
            raise ValueError("Cannot delete post while publishing")
        self.is_active = False

    def validate(self) -> list[str]:
        """
        Validate entity business rules

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.client_id:
            errors.append("client_id is required")

        if not self.account_id:
            errors.append("account_id is required")

        if not self.text_content:
            errors.append("text_content is required")

        if not self.content_type:
            errors.append("content_type is required")

        if not self.scheduled_date:
            errors.append("scheduled_date is required")

        if not self.scheduled_time:
            errors.append("scheduled_time is required")

        # Business rule: Cannot schedule in the past
        if self.scheduled_date and self.scheduled_time:
            scheduled_datetime = datetime.combine(
                self.scheduled_date,
                self.scheduled_time
            )
            if scheduled_datetime < datetime.now():
                errors.append("Cannot schedule posts in the past")

        return errors
