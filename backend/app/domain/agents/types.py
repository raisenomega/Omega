"""
Agent Domain Types
Enums and value objects for agents domain
Filosofía: No velocity, only precision 🐢💎
"""
from enum import Enum
from typing import Literal


class AgentStatus(str, Enum):
    """Agent operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ExecutionStatus(str, Enum):
    """Execution status tracking"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, Enum):
    """Log severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Department(str, Enum):
    """Agent departments"""
    NUCLEO = "núcleo"
    CONTENIDO = "contenido"
    VIDEO = "video"
    CONTEXTO = "contexto"
    PUBLICACION = "publicación"
    ANALYTICS = "analytics"


# Type aliases for clarity
AgentStatusType = Literal["active", "inactive", "maintenance"]
ExecutionStatusType = Literal["pending", "running", "completed", "failed", "cancelled"]
LogLevelType = Literal["debug", "info", "warning", "error", "critical"]
DepartmentType = Literal["núcleo", "contenido", "video", "contexto", "publicación", "analytics"]
