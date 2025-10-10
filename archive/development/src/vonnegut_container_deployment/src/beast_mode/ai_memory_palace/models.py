"""
Core data models for AI Memory Palace context persistence.

Implements SessionContext, ContextEvent, and ProjectState with proper serialization
for persistent storage and retrieval across AI conversation sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
import json
import uuid


class ContextEventType(Enum):
    """Types of context events that can be captured and persisted"""
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


@dataclass
class EventMetadata:
    """Metadata for context events"""
    source: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'tags': self.tags,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMetadata':
        return cls(
            source=data['source'],
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            tags=data.get('tags', []),
            confidence=data.get('confidence', 1.0)
        )


@dataclass
class ContextEvent:
    """Individual context event for persistence"""
    event_id: str
    event_type: ContextEventType
    timestamp: datetime
    correlation_id: str
    data: Dict[str, Any]
    metadata: EventMetadata
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'data': self.data,
            'metadata': self.metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextEvent':
        return cls(
            event_id=data['event_id'],
            event_type=ContextEventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            correlation_id=data['correlation_id'],
            data=data['data'],
            metadata=EventMetadata.from_dict(data['metadata'])
        )


@dataclass
class ServiceInfo:
    """Information about a running service"""
    name: str
    url: str
    status: str
    health_check_url: Optional[str] = None
    uptime_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'url': self.url,
            'status': self.status,
            'health_check_url': self.health_check_url,
            'uptime_seconds': self.uptime_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfo':
        return cls(
            name=data['name'],
            url=data['url'],
            status=data['status'],
            health_check_url=data.get('health_check_url'),
            uptime_seconds=data.get('uptime_seconds')
        )


@dataclass
class HealthStatus:
    """System health status information"""
    overall_status: str
    services_healthy: int
    services_total: int
    last_check: datetime
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall_status': self.overall_status,
            'services_healthy': self.services_healthy,
            'services_total': self.services_total,
            'last_check': self.last_check.isoformat(),
            'issues': self.issues
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthStatus':
        return cls(
            overall_status=data['overall_status'],
            services_healthy=data['services_healthy'],
            services_total=data['services_total'],
            last_check=datetime.fromisoformat(data['last_check']),
            issues=data.get('issues', [])
        )


@dataclass
class Change:
    """Represents a change made to the project"""
    change_id: str
    timestamp: datetime
    change_type: str
    description: str
    files_affected: List[str]
    author: Optional[str] = None
    
    def __post_init__(self):
        if not self.change_id:
            self.change_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'change_id': self.change_id,
            'timestamp': self.timestamp.isoformat(),
            'change_type': self.change_type,
            'description': self.description,
            'files_affected': self.files_affected,
            'author': self.author
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Change':
        return cls(
            change_id=data['change_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            change_type=data['change_type'],
            description=data['description'],
            files_affected=data['files_affected'],
            author=data.get('author')
        )


@dataclass
class SpecState:
    """State of a specification"""
    spec_name: str
    completion_percentage: float
    last_updated: datetime
    active_tasks: List[str]
    completed_tasks: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'spec_name': self.spec_name,
            'completion_percentage': self.completion_percentage,
            'last_updated': self.last_updated.isoformat(),
            'active_tasks': self.active_tasks,
            'completed_tasks': self.completed_tasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpecState':
        return cls(
            spec_name=data['spec_name'],
            completion_percentage=data['completion_percentage'],
            last_updated=datetime.fromisoformat(data['last_updated']),
            active_tasks=data['active_tasks'],
            completed_tasks=data['completed_tasks']
        )


@dataclass
class ProjectState:
    """Current state of the project"""
    architecture_overview: str
    running_services: List[ServiceInfo]
    active_specs: List[str]
    recent_changes: List[Change]
    health_status: HealthStatus
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'architecture_overview': self.architecture_overview,
            'running_services': [service.to_dict() for service in self.running_services],
            'active_specs': self.active_specs,
            'recent_changes': [change.to_dict() for change in self.recent_changes],
            'health_status': self.health_status.to_dict(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        return cls(
            architecture_overview=data['architecture_overview'],
            running_services=[ServiceInfo.from_dict(s) for s in data['running_services']],
            active_specs=data['active_specs'],
            recent_changes=[Change.from_dict(c) for c in data['recent_changes']],
            health_status=HealthStatus.from_dict(data['health_status']),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )


@dataclass
class ConversationEvent:
    """Individual conversation event"""
    timestamp: datetime
    event_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'content': self.content,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEvent':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            event_type=data['event_type'],
            content=data['content'],
            metadata=data.get('metadata', {})
        )


@dataclass
class Decision:
    """Represents a decision made during conversation"""
    decision_id: str
    timestamp: datetime
    description: str
    rationale: str
    alternatives_considered: List[str]
    outcome: Optional[str] = None
    
    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision_id': self.decision_id,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'rationale': self.rationale,
            'alternatives_considered': self.alternatives_considered,
            'outcome': self.outcome
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Decision':
        return cls(
            decision_id=data['decision_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data['description'],
            rationale=data['rationale'],
            alternatives_considered=data['alternatives_considered'],
            outcome=data.get('outcome')
        )


@dataclass
class WorkItem:
    """Represents work completed during conversation"""
    work_id: str
    timestamp: datetime
    work_type: str
    description: str
    files_created: List[str]
    files_modified: List[str]
    tests_added: List[str]
    
    def __post_init__(self):
        if not self.work_id:
            self.work_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'work_id': self.work_id,
            'timestamp': self.timestamp.isoformat(),
            'work_type': self.work_type,
            'description': self.description,
            'files_created': self.files_created,
            'files_modified': self.files_modified,
            'tests_added': self.tests_added
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkItem':
        return cls(
            work_id=data['work_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            work_type=data['work_type'],
            description=data['description'],
            files_created=data['files_created'],
            files_modified=data['files_modified'],
            tests_added=data['tests_added']
        )


@dataclass
class Discovery:
    """Represents a system discovery made during conversation"""
    discovery_id: str
    timestamp: datetime
    discovery_type: str
    description: str
    components_found: List[str]
    capabilities_identified: List[str]
    
    def __post_init__(self):
        if not self.discovery_id:
            self.discovery_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'discovery_id': self.discovery_id,
            'timestamp': self.timestamp.isoformat(),
            'discovery_type': self.discovery_type,
            'description': self.description,
            'components_found': self.components_found,
            'capabilities_identified': self.capabilities_identified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Discovery':
        return cls(
            discovery_id=data['discovery_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            discovery_type=data['discovery_type'],
            description=data['description'],
            components_found=data['components_found'],
            capabilities_identified=data['capabilities_identified']
        )


@dataclass
class SessionContext:
    """Complete context for an AI session"""
    project_id: str
    session_id: str
    timestamp: datetime
    conversation_history: List[ConversationEvent]
    project_state: ProjectState
    decisions_made: List[Decision]
    work_completed: List[WorkItem]
    system_discoveries: List[Discovery]
    spec_states: Dict[str, SpecState]
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_id': self.project_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'conversation_history': [event.to_dict() for event in self.conversation_history],
            'project_state': self.project_state.to_dict(),
            'decisions_made': [decision.to_dict() for decision in self.decisions_made],
            'work_completed': [work.to_dict() for work in self.work_completed],
            'system_discoveries': [discovery.to_dict() for discovery in self.system_discoveries],
            'spec_states': {name: spec.to_dict() for name, spec in self.spec_states.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        return cls(
            project_id=data['project_id'],
            session_id=data['session_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            conversation_history=[ConversationEvent.from_dict(e) for e in data['conversation_history']],
            project_state=ProjectState.from_dict(data['project_state']),
            decisions_made=[Decision.from_dict(d) for d in data['decisions_made']],
            work_completed=[WorkItem.from_dict(w) for w in data['work_completed']],
            system_discoveries=[Discovery.from_dict(d) for d in data['system_discoveries']],
            spec_states={name: SpecState.from_dict(spec) for name, spec in data['spec_states'].items()}
        )
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionContext':
        """Deserialize from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    def get_context_size(self) -> int:
        """Get approximate size of context in bytes"""
        return len(self.to_json().encode('utf-8'))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the context for quick overview"""
        return {
            'project_id': self.project_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'conversation_events': len(self.conversation_history),
            'decisions_made': len(self.decisions_made),
            'work_items': len(self.work_completed),
            'discoveries': len(self.system_discoveries),
            'active_specs': len(self.spec_states),
            'running_services': len(self.project_state.running_services),
            'context_size_bytes': self.get_context_size()
        }