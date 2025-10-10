#!/usr/bin/env python3
"""
Real-Time Models - Task 3.4 Implementation
===========================================

Data models and structures for real-time diagram updates.
Provides models for live component diagrams, WebSocket connection status,
live metrics flow, interactive sequence diagrams, and automated refresh.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json
import yaml
from pathlib import Path
import uuid


class UpdateTrigger(Enum):
    """Types of triggers for diagram updates."""
    INFRASTRUCTURE_CHANGE = "infrastructure_change"
    SERVICE_STATUS_CHANGE = "service_status_change"
    WEBSOCKET_CONNECTION_CHANGE = "websocket_connection_change"
    METRICS_THRESHOLD_EXCEEDED = "metrics_threshold_exceeded"
    MANUAL_REFRESH = "manual_refresh"
    SCHEDULED_REFRESH = "scheduled_refresh"
    ERROR_DETECTED = "error_detected"
    HEALTH_CHECK_FAILURE = "health_check_failure"


class RefreshStatus(Enum):
    """Status of diagram refresh operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ValidationLevel(Enum):
    """Levels of validation for real-time updates."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"
    NONE = "none"


@dataclass
class RealTimeStatus:
    """
    Real-time status information for a component or service.
    
    Provides live status indicators, health scores, and
    last update timestamps for real-time diagram updates.
    """
    component_id: str
    status: str
    health_score: float
    last_updated: datetime
    websocket_connected: bool = False
    metrics_available: bool = False
    error_count: int = 0
    warning_count: int = 0
    response_time_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_throughput: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "component_id": self.component_id,
            "status": self.status,
            "health_score": self.health_score,
            "last_updated": self.last_updated.isoformat(),
            "websocket_connected": self.websocket_connected,
            "metrics_available": self.metrics_available,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "response_time_ms": self.response_time_ms,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "network_throughput": self.network_throughput,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealTimeStatus':
        """Create from dictionary representation."""
        return cls(
            component_id=data["component_id"],
            status=data["status"],
            health_score=data["health_score"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
            websocket_connected=data.get("websocket_connected", False),
            metrics_available=data.get("metrics_available", False),
            error_count=data.get("error_count", 0),
            warning_count=data.get("warning_count", 0),
            response_time_ms=data.get("response_time_ms"),
            cpu_usage=data.get("cpu_usage"),
            memory_usage=data.get("memory_usage"),
            network_throughput=data.get("network_throughput"),
            metadata=data.get("metadata", {})
        )


@dataclass
class WebSocketConnectionStatus:
    """
    WebSocket connection status for real-time updates.
    
    Tracks connection state, message throughput, and
    connection health for WebSocket overlays.
    """
    endpoint: str
    connected: bool
    connection_time: Optional[datetime] = None
    last_message_time: Optional[datetime] = None
    messages_sent: int = 0
    messages_received: int = 0
    connection_errors: int = 0
    reconnect_attempts: int = 0
    latency_ms: Optional[float] = None
    bandwidth_kbps: Optional[float] = None
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "endpoint": self.endpoint,
            "connected": self.connected,
            "connection_time": self.connection_time.isoformat() if self.connection_time else None,
            "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "connection_errors": self.connection_errors,
            "reconnect_attempts": self.reconnect_attempts,
            "latency_ms": self.latency_ms,
            "bandwidth_kbps": self.bandwidth_kbps,
            "connection_id": self.connection_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketConnectionStatus':
        """Create from dictionary representation."""
        return cls(
            endpoint=data["endpoint"],
            connected=data["connected"],
            connection_time=datetime.fromisoformat(data["connection_time"]) if data.get("connection_time") else None,
            last_message_time=datetime.fromisoformat(data["last_message_time"]) if data.get("last_message_time") else None,
            messages_sent=data.get("messages_sent", 0),
            messages_received=data.get("messages_received", 0),
            connection_errors=data.get("connection_errors", 0),
            reconnect_attempts=data.get("reconnect_attempts", 0),
            latency_ms=data.get("latency_ms"),
            bandwidth_kbps=data.get("bandwidth_kbps"),
            connection_id=data.get("connection_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {})
        )


@dataclass
class LiveMetricsFlow:
    """
    Live metrics flow information for real-time data movement.
    
    Tracks metrics flow between components with real-time
    throughput and latency measurements.
    """
    source_component: str
    target_component: str
    metric_name: str
    flow_rate_per_second: float
    last_update: datetime
    latency_ms: Optional[float] = None
    data_size_bytes: Optional[int] = None
    error_rate: float = 0.0
    success_rate: float = 100.0
    flow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_component": self.source_component,
            "target_component": self.target_component,
            "metric_name": self.metric_name,
            "flow_rate_per_second": self.flow_rate_per_second,
            "last_update": self.last_update.isoformat(),
            "latency_ms": self.latency_ms,
            "data_size_bytes": self.data_size_bytes,
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
            "flow_id": self.flow_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LiveMetricsFlow':
        """Create from dictionary representation."""
        return cls(
            source_component=data["source_component"],
            target_component=data["target_component"],
            metric_name=data["metric_name"],
            flow_rate_per_second=data["flow_rate_per_second"],
            last_update=datetime.fromisoformat(data["last_update"]),
            latency_ms=data.get("latency_ms"),
            data_size_bytes=data.get("data_size_bytes"),
            error_rate=data.get("error_rate", 0.0),
            success_rate=data.get("success_rate", 100.0),
            flow_id=data.get("flow_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {})
        )


@dataclass
class InteractiveSequenceStep:
    """
    Interactive step in a sequence diagram for operational workflows.
    
    Represents a single step in an interactive sequence with
    real-time status and user interaction capabilities.
    """
    step_id: str
    participant: str
    action: str
    message: str
    timestamp: datetime
    status: str = "pending"
    duration_ms: Optional[float] = None
    user_interaction_required: bool = False
    validation_required: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "participant": self.participant,
            "action": self.action,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "duration_ms": self.duration_ms,
            "user_interaction_required": self.user_interaction_required,
            "validation_required": self.validation_required,
            "error_message": self.error_message,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractiveSequenceStep':
        """Create from dictionary representation."""
        return cls(
            step_id=data["step_id"],
            participant=data["participant"],
            action=data["action"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            status=data.get("status", "pending"),
            duration_ms=data.get("duration_ms"),
            user_interaction_required=data.get("user_interaction_required", False),
            validation_required=data.get("validation_required", False),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {})
        )


@dataclass
class DiagramRefreshRequest:
    """
    Request for diagram refresh with automated validation.
    
    Contains all information needed to refresh a diagram
    with real-time data and validation status.
    """
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    diagram_id: str = ""
    trigger: UpdateTrigger = UpdateTrigger.MANUAL_REFRESH
    requested_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"
    priority: int = 5  # 1-10 scale, 10 being highest
    validation_level: ValidationLevel = ValidationLevel.AUTOMATIC
    timeout_seconds: int = 3600  # 1 hour default
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "request_id": self.request_id,
            "diagram_id": self.diagram_id,
            "trigger": self.trigger.value,
            "requested_at": self.requested_at.isoformat(),
            "requested_by": self.requested_by,
            "priority": self.priority,
            "validation_level": self.validation_level.value,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramRefreshRequest':
        """Create from dictionary representation."""
        return cls(
            request_id=data.get("request_id", str(uuid.uuid4())),
            diagram_id=data.get("diagram_id", ""),
            trigger=UpdateTrigger(data.get("trigger", "manual_refresh")),
            requested_at=datetime.fromisoformat(data.get("requested_at", datetime.now().isoformat())),
            requested_by=data.get("requested_by", "system"),
            priority=data.get("priority", 5),
            validation_level=ValidationLevel(data.get("validation_level", "automatic")),
            timeout_seconds=data.get("timeout_seconds", 3600),
            metadata=data.get("metadata", {})
        )


@dataclass
class DiagramRefreshResult:
    """
    Result of diagram refresh operation with validation status.
    
    Contains the outcome of a diagram refresh including
    success status, validation results, and timestamps.
    """
    request_id: str
    diagram_id: str
    status: RefreshStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    validation_status: str = "pending"
    accuracy_confidence: float = 0.0
    components_updated: int = 0
    relationships_updated: int = 0
    websocket_statuses_updated: int = 0
    metrics_flows_updated: int = 0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "request_id": self.request_id,
            "diagram_id": self.diagram_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "validation_status": self.validation_status,
            "accuracy_confidence": self.accuracy_confidence,
            "components_updated": self.components_updated,
            "relationships_updated": self.relationships_updated,
            "websocket_statuses_updated": self.websocket_statuses_updated,
            "metrics_flows_updated": self.metrics_flows_updated,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramRefreshResult':
        """Create from dictionary representation."""
        return cls(
            request_id=data["request_id"],
            diagram_id=data["diagram_id"],
            status=RefreshStatus(data["status"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            duration_ms=data.get("duration_ms"),
            validation_status=data.get("validation_status", "pending"),
            accuracy_confidence=data.get("accuracy_confidence", 0.0),
            components_updated=data.get("components_updated", 0),
            relationships_updated=data.get("relationships_updated", 0),
            websocket_statuses_updated=data.get("websocket_statuses_updated", 0),
            metrics_flows_updated=data.get("metrics_flows_updated", 0),
            error_message=data.get("error_message"),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class RealTimeDiagramMetadata:
    """
    Comprehensive metadata for real-time diagram updates.
    
    Contains all metadata needed for real-time diagram management
    including refresh schedules, validation settings, and status tracking.
    """
    diagram_id: str
    title: str
    description: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    last_validated: Optional[datetime] = None
    validation_status: str = "pending"
    accuracy_confidence: float = 0.0
    refresh_interval_minutes: int = 60  # Default 1 hour
    auto_refresh_enabled: bool = True
    validation_level: ValidationLevel = ValidationLevel.AUTOMATIC
    real_time_statuses: Dict[str, RealTimeStatus] = field(default_factory=dict)
    websocket_connections: Dict[str, WebSocketConnectionStatus] = field(default_factory=dict)
    live_metrics_flows: List[LiveMetricsFlow] = field(default_factory=list)
    interactive_sequences: List[InteractiveSequenceStep] = field(default_factory=list)
    refresh_history: List[DiagramRefreshResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "diagram_id": self.diagram_id,
            "title": self.title,
            "description": self.description,
            "last_updated": self.last_updated.isoformat(),
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "validation_status": self.validation_status,
            "accuracy_confidence": self.accuracy_confidence,
            "refresh_interval_minutes": self.refresh_interval_minutes,
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "validation_level": self.validation_level.value,
            "real_time_statuses": {k: v.to_dict() for k, v in self.real_time_statuses.items()},
            "websocket_connections": {k: v.to_dict() for k, v in self.websocket_connections.items()},
            "live_metrics_flows": [flow.to_dict() for flow in self.live_metrics_flows],
            "interactive_sequences": [step.to_dict() for step in self.interactive_sequences],
            "refresh_history": [result.to_dict() for result in self.refresh_history],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealTimeDiagramMetadata':
        """Create from dictionary representation."""
        return cls(
            diagram_id=data["diagram_id"],
            title=data["title"],
            description=data.get("description"),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            last_validated=datetime.fromisoformat(data["last_validated"]) if data.get("last_validated") else None,
            validation_status=data.get("validation_status", "pending"),
            accuracy_confidence=data.get("accuracy_confidence", 0.0),
            refresh_interval_minutes=data.get("refresh_interval_minutes", 60),
            auto_refresh_enabled=data.get("auto_refresh_enabled", True),
            validation_level=ValidationLevel(data.get("validation_level", "automatic")),
            real_time_statuses={k: RealTimeStatus.from_dict(v) for k, v in data.get("real_time_statuses", {}).items()},
            websocket_connections={k: WebSocketConnectionStatus.from_dict(v) for k, v in data.get("websocket_connections", {}).items()},
            live_metrics_flows=[LiveMetricsFlow.from_dict(flow) for flow in data.get("live_metrics_flows", [])],
            interactive_sequences=[InteractiveSequenceStep.from_dict(step) for step in data.get("interactive_sequences", [])],
            refresh_history=[DiagramRefreshResult.from_dict(result) for result in data.get("refresh_history", [])],
            metadata=data.get("metadata", {})
        )
    
    def is_stale(self, threshold_minutes: int = 60) -> bool:
        """Check if diagram is stale based on last update time."""
        threshold = timedelta(minutes=threshold_minutes)
        return datetime.now() - self.last_updated > threshold
    
    def needs_refresh(self) -> bool:
        """Check if diagram needs refresh based on interval and staleness."""
        if not self.auto_refresh_enabled:
            return False
        
        interval = timedelta(minutes=self.refresh_interval_minutes)
        return datetime.now() - self.last_updated > interval
    
    def to_json(self, file_path: Optional[Path] = None) -> str:
        """Export to JSON format."""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
        
        return json_data
    
    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export to YAML format."""
        yaml_data = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(yaml_data)
        
        return yaml_data