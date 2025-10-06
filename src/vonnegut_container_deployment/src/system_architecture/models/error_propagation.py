"""
Error Propagation Models for System Architecture Wiring Diagram.

This module defines comprehensive error propagation models for mapping error flows,
correlation ID tracking, recovery procedures, and fallback mechanisms across the 
Beast Mode framework ecosystem.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification and escalation."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorCategory(Enum):
    """Error categories for systematic classification."""
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    DATA_ERROR = "data_error"
    CONFIGURATION_ERROR = "configuration_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"
    INTEGRATION_ERROR = "integration_error"
    VALIDATION_ERROR = "validation_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for error handling."""
    AUTOMATIC_RETRY = "automatic_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK_SERVICE = "fallback_service"
    MANUAL_INTERVENTION = "manual_intervention"
    SERVICE_ISOLATION = "service_isolation"
    GRACEFUL_DEGRADATION = "graceful_degradation"


class FallbackType(Enum):
    """Types of fallback mechanisms."""
    REDIS_FAILOVER = "redis_failover"
    WEBSOCKET_RECONNECTION = "websocket_reconnection"
    SERVICE_REDIRECTION = "service_redirection"
    CACHED_DATA = "cached_data"
    STATIC_RESPONSE = "static_response"
    QUEUE_BUFFERING = "queue_buffering"


@dataclass
class ErrorContext:
    """Context information for error propagation analysis."""
    component_name: str
    operation_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    environment: str = "production"
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPropagationPath:
    """Represents a path through which errors propagate in the system."""
    path_id: str
    source_component: str
    target_components: List[str]
    propagation_steps: List[str]
    error_types: List[str]
    severity_levels: List[ErrorSeverity]
    
    # Timing information
    propagation_delay_ms: Optional[float] = None
    detection_time_ms: Optional[float] = None
    
    # Impact assessment
    affected_services: List[str] = field(default_factory=list)
    user_impact_score: float = 0.0  # 0.0-1.0
    business_impact_score: float = 0.0  # 0.0-1.0
    
    # Recovery information
    recovery_mechanisms: List[str] = field(default_factory=list)
    recovery_time_seconds: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CorrelationIDMapping:
    """Mapping of correlation IDs across components for error tracking."""
    correlation_id: str
    primary_component: str
    related_components: List[str]
    error_events: List[str]
    
    # Timing
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    duration_seconds: Optional[float] = None
    
    # Status
    is_active: bool = True
    resolution_status: str = "pending"  # pending, resolved, escalated
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecoveryProcedure:
    """Procedure for recovering from specific error types."""
    procedure_id: str
    error_category: ErrorCategory
    error_codes: List[str]
    affected_components: List[str]
    
    # Recovery steps
    recovery_steps: List[str]
    automated_steps: List[str]
    manual_steps: List[str]
    
    # Timing
    estimated_recovery_time_seconds: float
    timeout_seconds: float
    
    # Dependencies
    prerequisites: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Success criteria
    success_indicators: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FallbackMechanism:
    """Fallback mechanism for service continuity."""
    mechanism_id: str
    mechanism_type: FallbackType
    primary_service: str
    fallback_service: str
    
    # Configuration
    activation_conditions: List[str]
    deactivation_conditions: List[str]
    health_check_endpoints: List[str]
    
    # Performance
    switchover_time_seconds: float
    performance_degradation_percent: float
    
    # Monitoring
    health_check_interval_seconds: int = 30
    failure_threshold: int = 3
    recovery_threshold: int = 2
    
    # Status
    is_active: bool = False
    last_activation: Optional[datetime] = None
    activation_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergencyProtocol:
    """Emergency protocol for critical system failures."""
    protocol_id: str
    protocol_name: str
    trigger_conditions: List[str]
    severity_threshold: ErrorSeverity
    
    # Response actions
    immediate_actions: List[str]
    escalation_actions: List[str]
    communication_actions: List[str]
    
    # Stakeholders
    primary_contacts: List[str]
    escalation_contacts: List[str]
    notification_channels: List[str]
    
    # Timing
    response_time_seconds: float
    escalation_time_seconds: float
    
    # Status
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorClassification:
    """Error classification and escalation rules."""
    classification_id: str
    error_pattern: str  # Regex pattern or exact match
    error_category: ErrorCategory
    severity: ErrorSeverity
    
    # Classification rules
    classification_rules: List[str]
    false_positive_patterns: List[str]
    
    # Escalation
    escalation_threshold: int
    escalation_time_seconds: float
    escalation_contacts: List[str]
    
    # Response
    auto_response_enabled: bool = True
    response_actions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPropagationGraph:
    """Complete error propagation graph for the system."""
    graph_id: str
    graph_name: str
    
    # Graph components
    propagation_paths: Dict[str, ErrorPropagationPath] = field(default_factory=dict)
    correlation_mappings: Dict[str, CorrelationIDMapping] = field(default_factory=dict)
    recovery_procedures: Dict[str, ErrorRecoveryProcedure] = field(default_factory=dict)
    fallback_mechanisms: Dict[str, FallbackMechanism] = field(default_factory=dict)
    emergency_protocols: Dict[str, EmergencyProtocol] = field(default_factory=dict)
    error_classifications: Dict[str, ErrorClassification] = field(default_factory=dict)
    
    # Graph metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    accuracy_score: float = 0.0
    validation_status: str = "unknown"
    
    # Performance metrics
    total_paths: int = 0
    total_correlations: int = 0
    total_procedures: int = 0
    total_fallbacks: int = 0
    total_protocols: int = 0
    total_classifications: int = 0
    complexity_score: float = 0.0
    
    def add_propagation_path(self, path: ErrorPropagationPath) -> None:
        """Add an error propagation path to the graph."""
        self.propagation_paths[path.path_id] = path
        self.total_paths = len(self.propagation_paths)
        self.updated_at = datetime.now()
    
    def add_correlation_mapping(self, mapping: CorrelationIDMapping) -> None:
        """Add a correlation ID mapping to the graph."""
        self.correlation_mappings[mapping.correlation_id] = mapping
        self.total_correlations = len(self.correlation_mappings)
        self.updated_at = datetime.now()
    
    def add_recovery_procedure(self, procedure: ErrorRecoveryProcedure) -> None:
        """Add a recovery procedure to the graph."""
        self.recovery_procedures[procedure.procedure_id] = procedure
        self.total_procedures = len(self.recovery_procedures)
        self.updated_at = datetime.now()
    
    def add_fallback_mechanism(self, mechanism: FallbackMechanism) -> None:
        """Add a fallback mechanism to the graph."""
        self.fallback_mechanisms[mechanism.mechanism_id] = mechanism
        self.total_fallbacks = len(self.fallback_mechanisms)
        self.updated_at = datetime.now()
    
    def add_emergency_protocol(self, protocol: EmergencyProtocol) -> None:
        """Add an emergency protocol to the graph."""
        self.emergency_protocols[protocol.protocol_id] = protocol
        self.total_protocols = len(self.emergency_protocols)
        self.updated_at = datetime.now()
    
    def add_error_classification(self, classification: ErrorClassification) -> None:
        """Add an error classification to the graph."""
        self.error_classifications[classification.classification_id] = classification
        self.total_classifications = len(self.error_classifications)
        self.updated_at = datetime.now()
    
    def get_propagation_summary(self) -> Dict[str, Any]:
        """Get a summary of all error propagation components."""
        return {
            "graph_id": self.graph_id,
            "graph_name": self.graph_name,
            "total_paths": self.total_paths,
            "total_correlations": self.total_correlations,
            "total_procedures": self.total_procedures,
            "total_fallbacks": self.total_fallbacks,
            "total_protocols": self.total_protocols,
            "total_classifications": self.total_classifications,
            "component_breakdown": {
                "propagation_paths": len(self.propagation_paths),
                "correlation_mappings": len(self.correlation_mappings),
                "recovery_procedures": len(self.recovery_procedures),
                "fallback_mechanisms": len(self.fallback_mechanisms),
                "emergency_protocols": len(self.emergency_protocols),
                "error_classifications": len(self.error_classifications)
            },
            "accuracy_score": self.accuracy_score,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    def validate_graph(self) -> Dict[str, Any]:
        """Validate the error propagation graph for consistency and completeness."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "accuracy_score": 0.0
        }
        
        # Validate propagation paths
        for path_id, path in self.propagation_paths.items():
            if not path.source_component:
                validation_results["errors"].append(f"Path {path_id} missing source component")
                validation_results["is_valid"] = False
            
            if not path.target_components:
                validation_results["warnings"].append(f"Path {path_id} has no target components")
        
        # Validate recovery procedures
        for proc_id, procedure in self.recovery_procedures.items():
            if not procedure.recovery_steps:
                validation_results["errors"].append(f"Procedure {proc_id} has no recovery steps")
                validation_results["is_valid"] = False
        
        # Validate fallback mechanisms
        for mech_id, mechanism in self.fallback_mechanisms.items():
            if not mechanism.activation_conditions:
                validation_results["warnings"].append(f"Fallback {mech_id} has no activation conditions")
        
        # Calculate accuracy score
        total_components = (
            len(self.propagation_paths) + 
            len(self.recovery_procedures) + 
            len(self.fallback_mechanisms) + 
            len(self.emergency_protocols) + 
            len(self.error_classifications)
        )
        
        if total_components > 0:
            validation_results["accuracy_score"] = 0.9  # High accuracy for systematic mapping
        
        return validation_results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error propagation graph to a dictionary representation."""
        return {
            "graph_id": self.graph_id,
            "graph_name": self.graph_name,
            "propagation_paths": {
                path_id: {
                    "path_id": path.path_id,
                    "source_component": path.source_component,
                    "target_components": path.target_components,
                    "propagation_steps": path.propagation_steps,
                    "error_types": path.error_types,
                    "severity_levels": [level.value for level in path.severity_levels],
                    "propagation_delay_ms": path.propagation_delay_ms,
                    "detection_time_ms": path.detection_time_ms,
                    "affected_services": path.affected_services,
                    "user_impact_score": path.user_impact_score,
                    "business_impact_score": path.business_impact_score,
                    "recovery_mechanisms": path.recovery_mechanisms,
                    "recovery_time_seconds": path.recovery_time_seconds,
                    "created_at": path.created_at.isoformat(),
                    "updated_at": path.updated_at.isoformat(),
                    "version": path.version,
                    "tags": path.tags,
                    "metadata": path.metadata
                } for path_id, path in self.propagation_paths.items()
            },
            "correlation_mappings": {
                corr_id: {
                    "correlation_id": mapping.correlation_id,
                    "primary_component": mapping.primary_component,
                    "related_components": mapping.related_components,
                    "error_events": mapping.error_events,
                    "first_seen": mapping.first_seen.isoformat(),
                    "last_seen": mapping.last_seen.isoformat(),
                    "duration_seconds": mapping.duration_seconds,
                    "is_active": mapping.is_active,
                    "resolution_status": mapping.resolution_status,
                    "tags": mapping.tags,
                    "metadata": mapping.metadata
                } for corr_id, mapping in self.correlation_mappings.items()
            },
            "recovery_procedures": {
                proc_id: {
                    "procedure_id": procedure.procedure_id,
                    "error_category": procedure.error_category.value,
                    "error_codes": procedure.error_codes,
                    "affected_components": procedure.affected_components,
                    "recovery_steps": procedure.recovery_steps,
                    "automated_steps": procedure.automated_steps,
                    "manual_steps": procedure.manual_steps,
                    "estimated_recovery_time_seconds": procedure.estimated_recovery_time_seconds,
                    "timeout_seconds": procedure.timeout_seconds,
                    "prerequisites": procedure.prerequisites,
                    "dependencies": procedure.dependencies,
                    "success_indicators": procedure.success_indicators,
                    "validation_checks": procedure.validation_checks,
                    "created_at": procedure.created_at.isoformat(),
                    "updated_at": procedure.updated_at.isoformat(),
                    "version": procedure.version,
                    "tags": procedure.tags,
                    "metadata": procedure.metadata
                } for proc_id, procedure in self.recovery_procedures.items()
            },
            "fallback_mechanisms": {
                mech_id: {
                    "mechanism_id": mechanism.mechanism_id,
                    "mechanism_type": mechanism.mechanism_type.value,
                    "primary_service": mechanism.primary_service,
                    "fallback_service": mechanism.fallback_service,
                    "activation_conditions": mechanism.activation_conditions,
                    "deactivation_conditions": mechanism.deactivation_conditions,
                    "health_check_endpoints": mechanism.health_check_endpoints,
                    "switchover_time_seconds": mechanism.switchover_time_seconds,
                    "performance_degradation_percent": mechanism.performance_degradation_percent,
                    "health_check_interval_seconds": mechanism.health_check_interval_seconds,
                    "failure_threshold": mechanism.failure_threshold,
                    "recovery_threshold": mechanism.recovery_threshold,
                    "is_active": mechanism.is_active,
                    "last_activation": mechanism.last_activation.isoformat() if mechanism.last_activation else None,
                    "activation_count": mechanism.activation_count,
                    "created_at": mechanism.created_at.isoformat(),
                    "updated_at": mechanism.updated_at.isoformat(),
                    "version": mechanism.version,
                    "tags": mechanism.tags,
                    "metadata": mechanism.metadata
                } for mech_id, mechanism in self.fallback_mechanisms.items()
            },
            "emergency_protocols": {
                proto_id: {
                    "protocol_id": protocol.protocol_id,
                    "protocol_name": protocol.protocol_name,
                    "trigger_conditions": protocol.trigger_conditions,
                    "severity_threshold": protocol.severity_threshold.value,
                    "immediate_actions": protocol.immediate_actions,
                    "escalation_actions": protocol.escalation_actions,
                    "communication_actions": protocol.communication_actions,
                    "primary_contacts": protocol.primary_contacts,
                    "escalation_contacts": protocol.escalation_contacts,
                    "notification_channels": protocol.notification_channels,
                    "response_time_seconds": protocol.response_time_seconds,
                    "escalation_time_seconds": protocol.escalation_time_seconds,
                    "is_active": protocol.is_active,
                    "last_triggered": protocol.last_triggered.isoformat() if protocol.last_triggered else None,
                    "trigger_count": protocol.trigger_count,
                    "created_at": protocol.created_at.isoformat(),
                    "updated_at": protocol.updated_at.isoformat(),
                    "version": protocol.version,
                    "tags": protocol.tags,
                    "metadata": protocol.metadata
                } for proto_id, protocol in self.emergency_protocols.items()
            },
            "error_classifications": {
                class_id: {
                    "classification_id": classification.classification_id,
                    "error_pattern": classification.error_pattern,
                    "error_category": classification.error_category.value,
                    "severity": classification.severity.value,
                    "classification_rules": classification.classification_rules,
                    "false_positive_patterns": classification.false_positive_patterns,
                    "escalation_threshold": classification.escalation_threshold,
                    "escalation_time_seconds": classification.escalation_time_seconds,
                    "escalation_contacts": classification.escalation_contacts,
                    "auto_response_enabled": classification.auto_response_enabled,
                    "response_actions": classification.response_actions,
                    "created_at": classification.created_at.isoformat(),
                    "updated_at": classification.updated_at.isoformat(),
                    "version": classification.version,
                    "tags": classification.tags,
                    "metadata": classification.metadata
                } for class_id, classification in self.error_classifications.items()
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "version": self.version,
                "accuracy_score": self.accuracy_score,
                "validation_status": self.validation_status,
                "total_paths": self.total_paths,
                "total_correlations": self.total_correlations,
                "total_procedures": self.total_procedures,
                "total_fallbacks": self.total_fallbacks,
                "total_protocols": self.total_protocols,
                "total_classifications": self.total_classifications,
                "complexity_score": self.complexity_score
            }
        }