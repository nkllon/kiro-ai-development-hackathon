"""
Data Flow Models for System Architecture Wiring Diagram.

This module defines comprehensive data flow models for mapping metrics, WebSocket streams,
error handling, and integration flows across the Beast Mode framework ecosystem.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


class DataFlowType(Enum):
    """Types of data flows in the system."""
    METRICS = "metrics"
    WEBSOCKET_STREAM = "websocket_stream"
    ERROR_PROPAGATION = "error_propagation"
    INTEGRATION_FLOW = "integration_flow"
    ACHIEVEMENT_FLOW = "achievement_flow"
    ANOMALY_DETECTION = "anomaly_detection"
    HEALTH_CHECK = "health_check"
    CONFIGURATION_SYNC = "configuration_sync"


class FlowDirection(Enum):
    """Direction of data flow."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class FlowPriority(Enum):
    """Priority levels for data flows."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class DataFlowNode:
    """Represents a node in the data flow graph."""
    node_id: str
    node_name: str
    node_type: str  # ReflectiveModule, Observatory, Prometheus, Grafana, etc.
    endpoint: Optional[str] = None
    port: Optional[int] = None
    health_endpoint: Optional[str] = None
    websocket_endpoints: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning and validation
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: str = "unknown"
    accuracy_score: float = 0.0


@dataclass
class DataFlowEdge:
    """Represents an edge (connection) in the data flow graph."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    flow_type: DataFlowType
    direction: FlowDirection
    priority: FlowPriority = FlowPriority.NORMAL
    
    # Flow characteristics
    data_format: str = "json"  # json, protobuf, binary, etc.
    transport_protocol: str = "http"  # http, websocket, tcp, udp
    compression_enabled: bool = False
    encryption_enabled: bool = False
    
    # Performance metrics
    latency_ms: Optional[float] = None
    throughput_per_second: Optional[float] = None
    error_rate_percent: Optional[float] = None
    success_rate_percent: Optional[float] = None
    
    # Configuration
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[float] = None
    batch_size: Optional[int] = None
    correlation_id_tracking: bool = True
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class MetricsFlow:
    """Represents metrics data flow from ReflectiveModule components to Observatory to Prometheus to Grafana."""
    flow_id: str
    source_component: str
    target_systems: List[str]  # Observatory, Prometheus, Grafana
    
    # Metrics characteristics
    metrics_types: List[str]  # health_score, uptime, error_count, etc.
    collection_interval_seconds: float = 15.0
    retention_period_days: int = 30
    
    # Flow path
    flow_path: List[str] = field(default_factory=list)  # [ReflectiveModule, Observatory, Prometheus, Grafana]
    parallel_streams: List[str] = field(default_factory=list)  # WebSocket real-time streams
    
    # Performance characteristics
    batch_collection_enabled: bool = True
    real_time_streaming_enabled: bool = True
    compression_enabled: bool = True
    
    # Error handling
    error_correlation_id: str = field(default_factory=lambda: str(uuid4()))
    error_propagation_path: List[str] = field(default_factory=list)
    fallback_mechanisms: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class WebSocketFlow:
    """Represents WebSocket real-time metrics streaming parallel to batch collection."""
    flow_id: str
    endpoint: str  # /ws/observatory, /ws/anomalies, /ws/emoji-rain, /ws/doctor-status
    
    # Streaming characteristics
    message_types: List[str]  # metrics, anomalies, achievements, health_status
    streaming_frequency_ms: int = 1000
    message_format: str = "json"
    compression_enabled: bool = True
    
    # Parallel processing
    parallel_to_batch: bool = True
    batch_collection_endpoint: Optional[str] = None
    real_time_endpoint: Optional[str] = None
    
    # Connection management
    connection_pool_size: int = 5
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    heartbeat_interval_seconds: int = 30
    
    # Performance metrics
    messages_per_second: Optional[float] = None
    connection_uptime_percent: Optional[float] = None
    message_loss_rate_percent: Optional[float] = None
    
    # Error handling
    error_correlation_id: str = field(default_factory=lambda: str(uuid4()))
    reconnection_strategy: str = "exponential_backoff"
    fallback_to_batch: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class ErrorFlow:
    """Represents systematic error handling with correlation ID tracking."""
    error_id: str
    correlation_id: str
    error_type: str
    severity: ErrorSeverity
    
    # Error propagation
    source_component: str
    propagation_path: List[str]
    affected_components: List[str]
    
    # Error details
    error_message: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    occurred_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution_time_seconds: Optional[float] = None
    
    # Recovery
    recovery_actions: List[str] = field(default_factory=list)
    fallback_activated: bool = False
    manual_intervention_required: bool = False
    
    # Impact assessment
    impact_score: float = 0.0  # 0.0-1.0
    affected_users: int = 0
    service_degradation: bool = False
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationFlow:
    """Represents integration flow mapping (ACE Reporter → AI Memory Palace → DAG Registry)."""
    flow_id: str
    integration_name: str
    source_system: str
    target_systems: List[str]
    
    # Integration characteristics
    integration_type: str  # data_sync, event_broadcast, state_replication
    data_format: str = "json"
    transport_protocol: str = "http"
    
    # Flow sequence
    flow_sequence: List[str] = field(default_factory=list)  # [ACE Reporter, AI Memory Palace, DAG Registry]
    dependencies: List[str] = field(default_factory=list)
    
    # Processing
    processing_mode: str = "sequential"  # sequential, parallel, pipeline
    batch_processing_enabled: bool = True
    real_time_processing_enabled: bool = True
    
    # Error handling
    error_correlation_id: str = field(default_factory=lambda: str(uuid4()))
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker_enabled: bool = True
    
    # Performance
    throughput_per_second: Optional[float] = None
    latency_ms: Optional[float] = None
    success_rate_percent: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class WebSocketMessageFlow:
    """Represents WebSocket message flows (/ws/anomalies → Grafana alerts)."""
    flow_id: str
    source_endpoint: str  # /ws/anomalies
    target_system: str  # Grafana
    
    # Message characteristics
    message_type: str  # anomaly_alert, health_status, metrics_update
    message_format: str = "json"
    priority: FlowPriority = FlowPriority.HIGH
    
    # Flow characteristics
    real_time_enabled: bool = True
    batch_processing_enabled: bool = False
    compression_enabled: bool = True
    
    # Alert processing
    alert_rules: List[Dict[str, Any]] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)
    escalation_policy: Optional[Dict[str, Any]] = None
    
    # Performance
    message_delivery_time_ms: Optional[float] = None
    alert_response_time_ms: Optional[float] = None
    false_positive_rate_percent: Optional[float] = None
    
    # Error handling
    error_correlation_id: str = field(default_factory=lambda: str(uuid4()))
    fallback_notification: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class EmojiRainFlow:
    """Represents emoji rain data flow (achievement → WebSocket → frontend)."""
    flow_id: str
    achievement_type: str
    trigger_event: str
    
    # Flow path
    flow_path: List[str] = field(default_factory=list)  # [achievement_detection, WebSocket, frontend]
    websocket_endpoint: str = "/ws/emoji-rain"
    
    # Emoji characteristics
    emoji_type: str = "celebration"
    emoji_sequence: List[str] = field(default_factory=list)
    animation_duration_ms: int = 3000
    
    # Broadcasting
    broadcast_scope: str = "global"  # global, user_specific, team_specific
    target_users: List[str] = field(default_factory=list)
    broadcast_channels: List[str] = field(default_factory=list)
    
    # Performance
    broadcast_latency_ms: Optional[float] = None
    delivery_success_rate_percent: Optional[float] = None
    user_engagement_score: Optional[float] = None
    
    # Error handling
    error_correlation_id: str = field(default_factory=lambda: str(uuid4()))
    fallback_celebration: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class DataFlowGraph:
    """Complete data flow graph representing all flows in the system."""
    graph_id: str
    graph_name: str
    
    # Graph components
    nodes: Dict[str, DataFlowNode] = field(default_factory=dict)
    edges: Dict[str, DataFlowEdge] = field(default_factory=dict)
    
    # Specific flow types
    metrics_flows: Dict[str, MetricsFlow] = field(default_factory=dict)
    websocket_flows: Dict[str, WebSocketFlow] = field(default_factory=dict)
    error_flows: Dict[str, ErrorFlow] = field(default_factory=dict)
    integration_flows: Dict[str, IntegrationFlow] = field(default_factory=dict)
    websocket_message_flows: Dict[str, WebSocketMessageFlow] = field(default_factory=dict)
    emoji_rain_flows: Dict[str, EmojiRainFlow] = field(default_factory=dict)
    
    # Graph metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"
    
    # Performance metrics
    total_nodes: int = 0
    total_edges: int = 0
    total_flows: int = 0
    complexity_score: float = 0.0
    
    def add_node(self, node: DataFlowNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        self.total_nodes = len(self.nodes)
        self.updated_at = datetime.now()
    
    def add_edge(self, edge: DataFlowEdge) -> None:
        """Add an edge to the graph."""
        self.edges[edge.edge_id] = edge
        self.total_edges = len(self.edges)
        self.updated_at = datetime.now()
    
    def add_metrics_flow(self, flow: MetricsFlow) -> None:
        """Add a metrics flow to the graph."""
        self.metrics_flows[flow.flow_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def add_websocket_flow(self, flow: WebSocketFlow) -> None:
        """Add a WebSocket flow to the graph."""
        self.websocket_flows[flow.flow_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def add_error_flow(self, flow: ErrorFlow) -> None:
        """Add an error flow to the graph."""
        self.error_flows[flow.error_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def add_integration_flow(self, flow: IntegrationFlow) -> None:
        """Add an integration flow to the graph."""
        self.integration_flows[flow.flow_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def add_websocket_message_flow(self, flow: WebSocketMessageFlow) -> None:
        """Add a WebSocket message flow to the graph."""
        self.websocket_message_flows[flow.flow_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def add_emoji_rain_flow(self, flow: EmojiRainFlow) -> None:
        """Add an emoji rain flow to the graph."""
        self.emoji_rain_flows[flow.flow_id] = flow
        self.total_flows = (
            len(self.metrics_flows) + 
            len(self.websocket_flows) + 
            len(self.error_flows) + 
            len(self.integration_flows) + 
            len(self.websocket_message_flows) + 
            len(self.emoji_rain_flows)
        )
        self.updated_at = datetime.now()
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get a summary of all flows in the graph."""
        return {
            "graph_id": self.graph_id,
            "graph_name": self.graph_name,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "total_flows": self.total_flows,
            "flow_breakdown": {
                "metrics_flows": len(self.metrics_flows),
                "websocket_flows": len(self.websocket_flows),
                "error_flows": len(self.error_flows),
                "integration_flows": len(self.integration_flows),
                "websocket_message_flows": len(self.websocket_message_flows),
                "emoji_rain_flows": len(self.emoji_rain_flows)
            },
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    def validate_graph(self) -> Dict[str, Any]:
        """Validate the data flow graph for consistency and completeness."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "accuracy_score": 0.0
        }
        
        # Validate nodes
        for node_id, node in self.nodes.items():
            if not node.node_name:
                validation_results["errors"].append(f"Node {node_id} missing name")
                validation_results["is_valid"] = False
            
            if node.accuracy_score < 0.5:
                validation_results["warnings"].append(f"Node {node_id} has low accuracy score: {node.accuracy_score}")
        
        # Validate edges
        for edge_id, edge in self.edges.items():
            if edge.source_node_id not in self.nodes:
                validation_results["errors"].append(f"Edge {edge_id} references unknown source node: {edge.source_node_id}")
                validation_results["is_valid"] = False
            
            if edge.target_node_id not in self.nodes:
                validation_results["errors"].append(f"Edge {edge_id} references unknown target node: {edge.target_node_id}")
                validation_results["is_valid"] = False
        
        # Calculate accuracy score
        if self.nodes:
            total_accuracy = sum(node.accuracy_score for node in self.nodes.values())
            validation_results["accuracy_score"] = total_accuracy / len(self.nodes)
        
        return validation_results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data flow graph to a dictionary representation."""
        return {
            "graph_id": self.graph_id,
            "graph_name": self.graph_name,
            "nodes": {node_id: {
                "node_id": node.node_id,
                "node_name": node.node_name,
                "node_type": node.node_type,
                "endpoint": node.endpoint,
                "port": node.port,
                "health_endpoint": node.health_endpoint,
                "websocket_endpoints": node.websocket_endpoints,
                "capabilities": node.capabilities,
                "dependencies": node.dependencies,
                "metadata": node.metadata,
                "created_at": node.created_at.isoformat(),
                "updated_at": node.updated_at.isoformat(),
                "version": node.version,
                "validation_status": node.validation_status,
                "accuracy_score": node.accuracy_score
            } for node_id, node in self.nodes.items()},
            "edges": {edge_id: {
                "edge_id": edge.edge_id,
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "flow_type": edge.flow_type.value,
                "direction": edge.direction.value,
                "priority": edge.priority.value,
                "data_format": edge.data_format,
                "transport_protocol": edge.transport_protocol,
                "compression_enabled": edge.compression_enabled,
                "encryption_enabled": edge.encryption_enabled,
                "latency_ms": edge.latency_ms,
                "throughput_per_second": edge.throughput_per_second,
                "error_rate_percent": edge.error_rate_percent,
                "success_rate_percent": edge.success_rate_percent,
                "retry_policy": edge.retry_policy,
                "timeout_seconds": edge.timeout_seconds,
                "batch_size": edge.batch_size,
                "correlation_id_tracking": edge.correlation_id_tracking,
                "description": edge.description,
                "tags": edge.tags,
                "metadata": edge.metadata,
                "created_at": edge.created_at.isoformat(),
                "updated_at": edge.updated_at.isoformat(),
                "version": edge.version
            } for edge_id, edge in self.edges.items()},
            "metrics_flows": {flow_id: {
                "flow_id": flow.flow_id,
                "source_component": flow.source_component,
                "target_systems": flow.target_systems,
                "metrics_types": flow.metrics_types,
                "collection_interval_seconds": flow.collection_interval_seconds,
                "retention_period_days": flow.retention_period_days,
                "flow_path": flow.flow_path,
                "parallel_streams": flow.parallel_streams,
                "batch_collection_enabled": flow.batch_collection_enabled,
                "real_time_streaming_enabled": flow.real_time_streaming_enabled,
                "compression_enabled": flow.compression_enabled,
                "error_correlation_id": flow.error_correlation_id,
                "error_propagation_path": flow.error_propagation_path,
                "fallback_mechanisms": flow.fallback_mechanisms,
                "created_at": flow.created_at.isoformat(),
                "updated_at": flow.updated_at.isoformat(),
                "version": flow.version
            } for flow_id, flow in self.metrics_flows.items()},
            "websocket_flows": {flow_id: {
                "flow_id": flow.flow_id,
                "endpoint": flow.endpoint,
                "message_types": flow.message_types,
                "streaming_frequency_ms": flow.streaming_frequency_ms,
                "message_format": flow.message_format,
                "compression_enabled": flow.compression_enabled,
                "parallel_to_batch": flow.parallel_to_batch,
                "batch_collection_endpoint": flow.batch_collection_endpoint,
                "real_time_endpoint": flow.real_time_endpoint,
                "connection_pool_size": flow.connection_pool_size,
                "retry_policy": flow.retry_policy,
                "heartbeat_interval_seconds": flow.heartbeat_interval_seconds,
                "messages_per_second": flow.messages_per_second,
                "connection_uptime_percent": flow.connection_uptime_percent,
                "message_loss_rate_percent": flow.message_loss_rate_percent,
                "error_correlation_id": flow.error_correlation_id,
                "reconnection_strategy": flow.reconnection_strategy,
                "fallback_to_batch": flow.fallback_to_batch,
                "created_at": flow.created_at.isoformat(),
                "updated_at": flow.updated_at.isoformat(),
                "version": flow.version
            } for flow_id, flow in self.websocket_flows.items()},
            "error_flows": {error_id: {
                "error_id": error.error_id,
                "correlation_id": error.correlation_id,
                "error_type": error.error_type,
                "severity": error.severity.value,
                "source_component": error.source_component,
                "propagation_path": error.propagation_path,
                "affected_components": error.affected_components,
                "error_message": error.error_message,
                "error_code": error.error_code,
                "stack_trace": error.stack_trace,
                "context_data": error.context_data,
                "occurred_at": error.occurred_at.isoformat(),
                "resolved_at": error.resolved_at.isoformat() if error.resolved_at else None,
                "resolution_time_seconds": error.resolution_time_seconds,
                "recovery_actions": error.recovery_actions,
                "fallback_activated": error.fallback_activated,
                "manual_intervention_required": error.manual_intervention_required,
                "impact_score": error.impact_score,
                "affected_users": error.affected_users,
                "service_degradation": error.service_degradation,
                "tags": error.tags,
                "metadata": error.metadata
            } for error_id, error in self.error_flows.items()},
            "integration_flows": {flow_id: {
                "flow_id": flow.flow_id,
                "integration_name": flow.integration_name,
                "source_system": flow.source_system,
                "target_systems": flow.target_systems,
                "integration_type": flow.integration_type,
                "data_format": flow.data_format,
                "transport_protocol": flow.transport_protocol,
                "flow_sequence": flow.flow_sequence,
                "dependencies": flow.dependencies,
                "processing_mode": flow.processing_mode,
                "batch_processing_enabled": flow.batch_processing_enabled,
                "real_time_processing_enabled": flow.real_time_processing_enabled,
                "error_correlation_id": flow.error_correlation_id,
                "retry_policy": flow.retry_policy,
                "circuit_breaker_enabled": flow.circuit_breaker_enabled,
                "throughput_per_second": flow.throughput_per_second,
                "latency_ms": flow.latency_ms,
                "success_rate_percent": flow.success_rate_percent,
                "created_at": flow.created_at.isoformat(),
                "updated_at": flow.updated_at.isoformat(),
                "version": flow.version
            } for flow_id, flow in self.integration_flows.items()},
            "websocket_message_flows": {flow_id: {
                "flow_id": flow.flow_id,
                "source_endpoint": flow.source_endpoint,
                "target_system": flow.target_system,
                "message_type": flow.message_type,
                "message_format": flow.message_format,
                "priority": flow.priority.value,
                "real_time_enabled": flow.real_time_enabled,
                "batch_processing_enabled": flow.batch_processing_enabled,
                "compression_enabled": flow.compression_enabled,
                "alert_rules": flow.alert_rules,
                "notification_channels": flow.notification_channels,
                "escalation_policy": flow.escalation_policy,
                "message_delivery_time_ms": flow.message_delivery_time_ms,
                "alert_response_time_ms": flow.alert_response_time_ms,
                "false_positive_rate_percent": flow.false_positive_rate_percent,
                "error_correlation_id": flow.error_correlation_id,
                "fallback_notification": flow.fallback_notification,
                "created_at": flow.created_at.isoformat(),
                "updated_at": flow.updated_at.isoformat(),
                "version": flow.version
            } for flow_id, flow in self.websocket_message_flows.items()},
            "emoji_rain_flows": {flow_id: {
                "flow_id": flow.flow_id,
                "achievement_type": flow.achievement_type,
                "trigger_event": flow.trigger_event,
                "flow_path": flow.flow_path,
                "websocket_endpoint": flow.websocket_endpoint,
                "emoji_type": flow.emoji_type,
                "emoji_sequence": flow.emoji_sequence,
                "animation_duration_ms": flow.animation_duration_ms,
                "broadcast_scope": flow.broadcast_scope,
                "target_users": flow.target_users,
                "broadcast_channels": flow.broadcast_channels,
                "broadcast_latency_ms": flow.broadcast_latency_ms,
                "delivery_success_rate_percent": flow.delivery_success_rate_percent,
                "user_engagement_score": flow.user_engagement_score,
                "error_correlation_id": flow.error_correlation_id,
                "fallback_celebration": flow.fallback_celebration,
                "created_at": flow.created_at.isoformat(),
                "updated_at": flow.updated_at.isoformat(),
                "version": flow.version
            } for flow_id, flow in self.emoji_rain_flows.items()},
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "version": self.version,
                "accuracy_score": self.accuracy_score,
                "validation_status": self.validation_status,
                "total_nodes": self.total_nodes,
                "total_edges": self.total_edges,
                "total_flows": self.total_flows,
                "complexity_score": self.complexity_score
            }
        }