"""
AI Memory Palace Data Models

Core data structures for context management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ContextEventType(Enum):
    """Types of context events."""
    CONVERSATION_START = "conversation_start"
    CONVERSATION_END = "conversation_end"
    CODE_WRITTEN = "code_written"
    SPEC_CREATED = "spec_created"
    SPEC_UPDATED = "spec_updated"
    TASK_COMPLETED = "task_completed"
    DECISION_MADE = "decision_made"
    DISCOVERY_MADE = "discovery_made"
    ERROR_ENCOUNTERED = "error_encountered"
    SYSTEM_STATE_CHANGED = "system_state_changed"
    SERVICE_DISCOVERED = "service_discovered"
    SERVICE_HEALTH_CHANGED = "service_health_changed"
    CONFIGURATION_CHANGED = "configuration_changed"
    RUNTIME_STATE_UPDATED = "runtime_state_updated"


@dataclass
class ServiceInfo:
    """Information about a discovered service."""
    name: str
    host: str
    port: int
    health_status: str
    discovery_source: str  # "redis", "prometheus", "health_check"
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Service health status information."""
    status: str  # "healthy", "unhealthy", "unknown"
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class StalenessInfo:
    """Information about data staleness."""
    last_updated: datetime
    is_stale: bool
    staleness_threshold_seconds: int
    refresh_needed: bool


@dataclass
class ProjectState:
    """Current state of the project."""
    architecture_overview: str
    running_services: List[ServiceInfo] = field(default_factory=list)
    active_specs: List[str] = field(default_factory=list)
    recent_changes: List[str] = field(default_factory=list)
    health_status: str = "unknown"
    service_discovery_cache: Dict[str, ServiceInfo] = field(default_factory=dict)
    last_discovery_timestamp: Optional[datetime] = None
    staleness_indicators: Dict[str, StalenessInfo] = field(default_factory=dict)


@dataclass
class ContextEvent:
    """Individual context event for persistence."""
    event_id: str
    event_type: ContextEventType
    timestamp: datetime
    correlation_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Complete context for an AI session."""
    project_id: str
    session_id: str
    timestamp: datetime
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    project_state: Optional[ProjectState] = None
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    work_completed: List[Dict[str, Any]] = field(default_factory=list)
    system_discoveries: List[Dict[str, Any]] = field(default_factory=list)
    spec_states: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextSummary:
    """Summarized view of context for developer experience."""
    project_id: str
    last_session: datetime
    total_events: int
    recent_decisions: List[str]
    active_specs: List[str]
    system_health: str
    context_size_mb: float
