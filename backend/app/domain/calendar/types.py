"""
Calendar Domain Types
Enums and value objects for scheduled posts domain
Filosofía: No velocity, only precision 🐢💎
"""
from enum import Enum
from typing import Literal


class ContentTypeEnum(str, Enum):
    """Content type for social media posts"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"


class PostStatus(str, Enum):
    """Status of scheduled post"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


# Type aliases for clarity
ContentType = Literal["post", "story", "reel", "carousel"]
Status = Literal["draft", "scheduled", "publishing", "published", "failed"]
UserPlan = Literal["basico_97", "pro_197", "enterprise_497"]
