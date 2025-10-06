"""
Sequence Models for Observatory-Specific Sequence Diagrams - Task 3.2 Implementation
====================================================================================

Data models and structures for generating Observatory-specific sequence diagrams
including tunnel operations, dashboard lifecycle, WebSocket connections, and
emergency protocols.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


class SequenceType(Enum):
    """Types of sequence diagrams."""
    TUNNEL_START = "tunnel_start"
    TUNNEL_STOP = "tunnel_stop"
    DASHBOARD_UP = "dashboard_up"
    DASHBOARD_STOP = "dashboard_stop"
    DASHBOARD_RESTART = "dashboard_restart"
    DASHBOARD_STATUS = "dashboard_status"
    WEBSOCKET_CONNECTION = "websocket_connection"
    EMERGENCY_PROTOCOL = "emergency_protocol"
    HEALTH_CHECK = "health_check"
    DNS_PROPAGATION = "dns_propagation"


class ParticipantType(Enum):
    """Types of sequence diagram participants."""
    USER = "user"
    MAKEFILE = "makefile"
    PYTHON_SCRIPT = "python_script"
    OBSERVATORY_SERVER = "observatory_server"
    CLOUDFLARE_TUNNEL = "cloudflare_tunnel"
    DNS_SERVER = "dns_server"
    WEBSOCKET_CLIENT = "websocket_client"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    REDIS = "redis"
    REFLECTIVE_MODULE = "reflective_module"
    EMERGENCY_SYSTEM = "emergency_system"


class MessageType(Enum):
    """Types of messages in sequence diagrams."""
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    WEBSOCKET_CONNECT = "websocket_connect"
    WEBSOCKET_MESSAGE = "websocket_message"
    WEBSOCKET_DISCONNECT = "websocket_disconnect"
    DNS_QUERY = "dns_query"
    DNS_RESPONSE = "dns_response"
    HEALTH_CHECK = "health_check"
    METRICS_COLLECTION = "metrics_collection"
    ERROR_EVENT = "error_event"
    EMERGENCY_ACTIVATION = "emergency_activation"
    RECOVERY_ACTION = "recovery_action"


class TimingType(Enum):
    """Types of timing constraints."""
    IMMEDIATE = "immediate"
    FAST = "fast"  # < 1 second
    NORMAL = "normal"  # 1-5 seconds
    SLOW = "slow"  # 5-30 seconds
    VERY_SLOW = "very_slow"  # > 30 seconds


@dataclass
class SequenceParticipant:
    """Represents a participant in a sequence diagram."""
    participant_id: str
    participant_name: str
    participant_type: ParticipantType
    endpoint: Optional[str] = None
    port: Optional[int] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning and validation
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: str = "unknown"
    accuracy_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "participant_id": self.participant_id,
            "participant_name": self.participant_name,
            "participant_type": self.participant_type.value,
            "endpoint": self.endpoint,
            "port": self.port,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "validation_status": self.validation_status,
            "accuracy_score": self.accuracy_score
        }


@dataclass
class SequenceMessage:
    """Represents a message in a sequence diagram."""
    message_id: str
    source_participant_id: str
    target_participant_id: str
    message_type: MessageType
    message_content: str
    timing: TimingType = TimingType.NORMAL
    correlation_id: Optional[str] = None
    
    # Message characteristics
    is_async: bool = False
    is_error: bool = False
    retry_count: int = 0
    timeout_seconds: Optional[float] = None
    
    # Response handling
    expects_response: bool = True
    response_timeout_seconds: Optional[float] = None
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "source_participant_id": self.source_participant_id,
            "target_participant_id": self.target_participant_id,
            "message_type": self.message_type.value,
            "message_content": self.message_content,
            "timing": self.timing.value,
            "correlation_id": self.correlation_id,
            "is_async": self.is_async,
            "is_error": self.is_error,
            "retry_count": self.retry_count,
            "timeout_seconds": self.timeout_seconds,
            "expects_response": self.expects_response,
            "response_timeout_seconds": self.response_timeout_seconds,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }


@dataclass
class SequenceActivation:
    """Represents an activation period in a sequence diagram."""
    activation_id: str
    participant_id: str
    start_message_id: str
    end_message_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    is_concurrent: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "activation_id": self.activation_id,
            "participant_id": self.participant_id,
            "start_message_id": self.start_message_id,
            "end_message_id": self.end_message_id,
            "duration_seconds": self.duration_seconds,
            "is_concurrent": self.is_concurrent,
            "metadata": self.metadata
        }


@dataclass
class TunnelStartSequence:
    """Represents tunnel-start sequence with DNS propagation flows."""
    sequence_id: str
    sequence_name: str = "Tunnel Start Sequence"
    sequence_type: SequenceType = SequenceType.TUNNEL_START
    
    # Participants
    participants: List[SequenceParticipant] = field(default_factory=list)
    
    # Messages and flow
    messages: List[SequenceMessage] = field(default_factory=list)
    activations: List[SequenceActivation] = field(default_factory=list)
    
    # DNS propagation specific
    dns_propagation_steps: List[str] = field(default_factory=list)
    dns_propagation_timing: Dict[str, float] = field(default_factory=dict)
    
    # WebSocket connection establishment
    websocket_connection_steps: List[str] = field(default_factory=list)
    websocket_endpoints: List[str] = field(default_factory=list)
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    failure_scenarios: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_type": self.sequence_type.value,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "activations": [a.to_dict() for a in self.activations],
            "dns_propagation_steps": self.dns_propagation_steps,
            "dns_propagation_timing": self.dns_propagation_timing,
            "websocket_connection_steps": self.websocket_connection_steps,
            "websocket_endpoints": self.websocket_endpoints,
            "success_criteria": self.success_criteria,
            "failure_scenarios": self.failure_scenarios,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status
        }


@dataclass
class TunnelStopSequence:
    """Represents tunnel-stop sequence with graceful shutdown."""
    sequence_id: str
    sequence_name: str = "Tunnel Stop Sequence"
    sequence_type: SequenceType = SequenceType.TUNNEL_STOP
    
    # Participants
    participants: List[SequenceParticipant] = field(default_factory=list)
    
    # Messages and flow
    messages: List[SequenceMessage] = field(default_factory=list)
    activations: List[SequenceActivation] = field(default_factory=list)
    
    # Graceful shutdown steps
    shutdown_steps: List[str] = field(default_factory=list)
    cleanup_actions: List[str] = field(default_factory=list)
    
    # WebSocket disconnection
    websocket_disconnection_steps: List[str] = field(default_factory=list)
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    failure_scenarios: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_type": self.sequence_type.value,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "activations": [a.to_dict() for a in self.activations],
            "shutdown_steps": self.shutdown_steps,
            "cleanup_actions": self.cleanup_actions,
            "websocket_disconnection_steps": self.websocket_disconnection_steps,
            "success_criteria": self.success_criteria,
            "failure_scenarios": self.failure_scenarios,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status
        }


@dataclass
class DashboardLifecycleSequence:
    """Represents dashboard lifecycle sequences (up/stop/restart)."""
    sequence_id: str
    sequence_name: str
    sequence_type: SequenceType
    
    # Participants
    participants: List[SequenceParticipant] = field(default_factory=list)
    
    # Messages and flow
    messages: List[SequenceMessage] = field(default_factory=list)
    activations: List[SequenceActivation] = field(default_factory=list)
    
    # Observatory WebSocket endpoint registration
    websocket_endpoint_registration: List[str] = field(default_factory=list)
    websocket_endpoints: List[str] = field(default_factory=list)
    
    # ReflectiveModule initialization
    reflective_module_initialization: List[str] = field(default_factory=list)
    health_endpoints: List[str] = field(default_factory=list)
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    failure_scenarios: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_type": self.sequence_type.value,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "activations": [a.to_dict() for a in self.activations],
            "websocket_endpoint_registration": self.websocket_endpoint_registration,
            "websocket_endpoints": self.websocket_endpoints,
            "reflective_module_initialization": self.reflective_module_initialization,
            "health_endpoints": self.health_endpoints,
            "success_criteria": self.success_criteria,
            "failure_scenarios": self.failure_scenarios,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status
        }


@dataclass
class DashboardStatusSequence:
    """Represents dashboard-status comprehensive health check flow."""
    sequence_id: str
    sequence_name: str = "Dashboard Status Health Check"
    sequence_type: SequenceType = SequenceType.DASHBOARD_STATUS
    
    # Participants
    participants: List[SequenceParticipant] = field(default_factory=list)
    
    # Messages and flow
    messages: List[SequenceMessage] = field(default_factory=list)
    activations: List[SequenceActivation] = field(default_factory=list)
    
    # Health check components
    health_check_components: List[str] = field(default_factory=list)
    health_endpoints: List[str] = field(default_factory=list)
    
    # WebSocket connection health checks
    websocket_health_checks: List[str] = field(default_factory=list)
    websocket_endpoints: List[str] = field(default_factory=list)
    
    # Metrics collection validation
    metrics_collection_validation: List[str] = field(default_factory=list)
    prometheus_endpoints: List[str] = field(default_factory=list)
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    failure_scenarios: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_type": self.sequence_type.value,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "activations": [a.to_dict() for a in self.activations],
            "health_check_components": self.health_check_components,
            "health_endpoints": self.health_endpoints,
            "websocket_health_checks": self.websocket_health_checks,
            "websocket_endpoints": self.websocket_endpoints,
            "metrics_collection_validation": self.metrics_collection_validation,
            "prometheus_endpoints": self.prometheus_endpoints,
            "success_criteria": self.success_criteria,
            "failure_scenarios": self.failure_scenarios,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status
        }


@dataclass
class EmergencyProtocolSequence:
    """Represents emergency protocol activation and systematic recovery procedures."""
    sequence_id: str
    sequence_name: str = "Emergency Protocol Activation"
    sequence_type: SequenceType = SequenceType.EMERGENCY_PROTOCOL
    
    # Participants
    participants: List[SequenceParticipant] = field(default_factory=list)
    
    # Messages and flow
    messages: List[SequenceMessage] = field(default_factory=list)
    activations: List[SequenceActivation] = field(default_factory=list)
    
    # Emergency activation
    emergency_activation_steps: List[str] = field(default_factory=list)
    emergency_triggers: List[str] = field(default_factory=list)
    
    # Observatory emergency coordination workflows
    observatory_emergency_coordination: List[str] = field(default_factory=list)
    emergency_websocket_endpoints: List[str] = field(default_factory=list)
    
    # Systematic recovery procedures
    recovery_procedures: List[str] = field(default_factory=list)
    recovery_validation_steps: List[str] = field(default_factory=list)
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)
    failure_scenarios: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_name": self.sequence_name,
            "sequence_type": self.sequence_type.value,
            "participants": [p.to_dict() for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "activations": [a.to_dict() for a in self.activations],
            "emergency_activation_steps": self.emergency_activation_steps,
            "emergency_triggers": self.emergency_triggers,
            "observatory_emergency_coordination": self.observatory_emergency_coordination,
            "emergency_websocket_endpoints": self.emergency_websocket_endpoints,
            "recovery_procedures": self.recovery_procedures,
            "recovery_validation_steps": self.recovery_validation_steps,
            "success_criteria": self.success_criteria,
            "failure_scenarios": self.failure_scenarios,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status
        }


@dataclass
class ObservatorySequenceCollection:
    """Complete collection of Observatory-specific sequence diagrams."""
    collection_id: str
    collection_name: str = "Observatory Sequence Diagrams Collection"
    
    # Sequence diagrams
    tunnel_start_sequence: Optional[TunnelStartSequence] = None
    tunnel_stop_sequence: Optional[TunnelStopSequence] = None
    dashboard_up_sequence: Optional[DashboardLifecycleSequence] = None
    dashboard_stop_sequence: Optional[DashboardLifecycleSequence] = None
    dashboard_restart_sequence: Optional[DashboardLifecycleSequence] = None
    dashboard_status_sequence: Optional[DashboardStatusSequence] = None
    emergency_protocol_sequence: Optional[EmergencyProtocolSequence] = None
    
    # Collection metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"
    
    # Analysis metadata
    total_sequences: int = 0
    total_participants: int = 0
    total_messages: int = 0
    complexity_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "collection_id": self.collection_id,
            "collection_name": self.collection_name,
            "tunnel_start_sequence": self.tunnel_start_sequence.to_dict() if self.tunnel_start_sequence else None,
            "tunnel_stop_sequence": self.tunnel_stop_sequence.to_dict() if self.tunnel_stop_sequence else None,
            "dashboard_up_sequence": self.dashboard_up_sequence.to_dict() if self.dashboard_up_sequence else None,
            "dashboard_stop_sequence": self.dashboard_stop_sequence.to_dict() if self.dashboard_stop_sequence else None,
            "dashboard_restart_sequence": self.dashboard_restart_sequence.to_dict() if self.dashboard_restart_sequence else None,
            "dashboard_status_sequence": self.dashboard_status_sequence.to_dict() if self.dashboard_status_sequence else None,
            "emergency_protocol_sequence": self.emergency_protocol_sequence.to_dict() if self.emergency_protocol_sequence else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status,
            "total_sequences": self.total_sequences,
            "total_participants": self.total_participants,
            "total_messages": self.total_messages,
            "complexity_score": self.complexity_score
        }

    def get_sequence_summary(self) -> Dict[str, Any]:
        """Get summary of all sequences in the collection."""
        sequences = []
        
        if self.tunnel_start_sequence:
            sequences.append({
                "type": "tunnel_start",
                "participants": len(self.tunnel_start_sequence.participants),
                "messages": len(self.tunnel_start_sequence.messages),
                "accuracy_score": self.tunnel_start_sequence.accuracy_score
            })
        
        if self.tunnel_stop_sequence:
            sequences.append({
                "type": "tunnel_stop",
                "participants": len(self.tunnel_stop_sequence.participants),
                "messages": len(self.tunnel_stop_sequence.messages),
                "accuracy_score": self.tunnel_stop_sequence.accuracy_score
            })
        
        if self.dashboard_up_sequence:
            sequences.append({
                "type": "dashboard_up",
                "participants": len(self.dashboard_up_sequence.participants),
                "messages": len(self.dashboard_up_sequence.messages),
                "accuracy_score": self.dashboard_up_sequence.accuracy_score
            })
        
        if self.dashboard_stop_sequence:
            sequences.append({
                "type": "dashboard_stop",
                "participants": len(self.dashboard_stop_sequence.participants),
                "messages": len(self.dashboard_stop_sequence.messages),
                "accuracy_score": self.dashboard_stop_sequence.accuracy_score
            })
        
        if self.dashboard_restart_sequence:
            sequences.append({
                "type": "dashboard_restart",
                "participants": len(self.dashboard_restart_sequence.participants),
                "messages": len(self.dashboard_restart_sequence.messages),
                "accuracy_score": self.dashboard_restart_sequence.accuracy_score
            })
        
        if self.dashboard_status_sequence:
            sequences.append({
                "type": "dashboard_status",
                "participants": len(self.dashboard_status_sequence.participants),
                "messages": len(self.dashboard_status_sequence.messages),
                "accuracy_score": self.dashboard_status_sequence.accuracy_score
            })
        
        if self.emergency_protocol_sequence:
            sequences.append({
                "type": "emergency_protocol",
                "participants": len(self.emergency_protocol_sequence.participants),
                "messages": len(self.emergency_protocol_sequence.messages),
                "accuracy_score": self.emergency_protocol_sequence.accuracy_score
            })
        
        return {
            "collection_id": self.collection_id,
            "collection_name": self.collection_name,
            "total_sequences": len(sequences),
            "sequences": sequences,
            "overall_accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }

    def validate_collection(self) -> Dict[str, Any]:
        """Validate the sequence collection for consistency and completeness."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "accuracy_score": 0.0
        }
        
        # Validate sequences
        sequences = [
            self.tunnel_start_sequence,
            self.tunnel_stop_sequence,
            self.dashboard_up_sequence,
            self.dashboard_stop_sequence,
            self.dashboard_restart_sequence,
            self.dashboard_status_sequence,
            self.emergency_protocol_sequence
        ]
        
        valid_sequences = [seq for seq in sequences if seq is not None]
        
        if not valid_sequences:
            validation_results["errors"].append("No sequences defined in collection")
            validation_results["is_valid"] = False
        
        # Validate each sequence
        for sequence in valid_sequences:
            if not sequence.participants:
                validation_results["warnings"].append(f"Sequence {sequence.sequence_name} has no participants")
            
            if not sequence.messages:
                validation_results["warnings"].append(f"Sequence {sequence.sequence_name} has no messages")
            
            if sequence.accuracy_score < 0.5:
                validation_results["warnings"].append(f"Sequence {sequence.sequence_name} has low accuracy score: {sequence.accuracy_score}")
        
        # Calculate overall accuracy score
        if valid_sequences:
            total_accuracy = sum(seq.accuracy_score for seq in valid_sequences)
            validation_results["accuracy_score"] = total_accuracy / len(valid_sequences)
        
        return validation_results

    def to_json(self, file_path: Optional[str] = None) -> str:
        """Export collection to JSON format."""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
        
        return json_data

    def to_plantuml(self) -> str:
        """Export collection to PlantUML format."""
        plantuml_content = []
        plantuml_content.append("@startuml Observatory Sequence Diagrams")
        plantuml_content.append("")
        
        # Generate PlantUML for each sequence
        if self.tunnel_start_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.tunnel_start_sequence))
            plantuml_content.append("")
        
        if self.tunnel_stop_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.tunnel_stop_sequence))
            plantuml_content.append("")
        
        if self.dashboard_up_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.dashboard_up_sequence))
            plantuml_content.append("")
        
        if self.dashboard_stop_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.dashboard_stop_sequence))
            plantuml_content.append("")
        
        if self.dashboard_restart_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.dashboard_restart_sequence))
            plantuml_content.append("")
        
        if self.dashboard_status_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.dashboard_status_sequence))
            plantuml_content.append("")
        
        if self.emergency_protocol_sequence:
            plantuml_content.append(self._generate_plantuml_sequence(self.emergency_protocol_sequence))
            plantuml_content.append("")
        
        plantuml_content.append("@enduml")
        
        return "\n".join(plantuml_content)

    def _generate_plantuml_sequence(self, sequence) -> str:
        """Generate PlantUML content for a single sequence."""
        plantuml_lines = []
        
        # Title
        plantuml_lines.append(f"title {sequence.sequence_name}")
        plantuml_lines.append("")
        
        # Participants
        for participant in sequence.participants:
            plantuml_lines.append(f"participant \"{participant.participant_name}\" as {participant.participant_id}")
        
        plantuml_lines.append("")
        
        # Messages
        for message in sequence.messages:
            source = message.source_participant_id
            target = message.target_participant_id
            content = message.message_content
            
            if message.is_error:
                plantuml_lines.append(f"{source} -> {target} : **{content}**")
            else:
                plantuml_lines.append(f"{source} -> {target} : {content}")
        
        return "\n".join(plantuml_lines)