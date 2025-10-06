"""
Data models for Runtime State Registry

Defines the core data structures used throughout the Runtime State Registry
for representing multi-source system state, compliance, and reconciliation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


class ServiceStatus(Enum):
    """Service operational status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class CMSStatus(Enum):
    """CMS configuration status."""
    DEFINED = "defined"
    ORPHANED = "orphaned"
    MISSING = "missing"


class SpecStatus(Enum):
    """Specification compliance status."""
    SPECIFIED = "specified"
    UNSPECIFIED = "unspecified"
    SPEC_MISSING = "spec_missing"


class DriftType(Enum):
    """Types of configuration drift."""
    CONFIG_DRIFT = "config_drift"
    SPEC_DRIFT = "spec_drift"
    ORPHANED = "orphaned"
    MISSING = "missing"


class DriftSeverity(Enum):
    """Severity levels for configuration drift."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class StateLayer(Enum):
    """State layers in the three-layer model."""
    SPECIFICATION = "specification"
    CMS = "cms"
    RUNTIME = "runtime"


class ServiceHealth(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class EventType(Enum):
    """Types of state change events."""
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    CONFIG_CHANGE = "config_change"
    DRIFT_DETECTED = "drift_detected"
    COMPLIANCE_CHANGE = "compliance_change"
    REMEDIATION_ACTION = "remediation_action"


class ComplianceTrend(Enum):
    """Compliance score trend direction."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


class ReconciliationStatus(Enum):
    """Status of three-layer reconciliation."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


@dataclass
class RedisServiceData:
    """Service data from Redis sources."""
    health_key: Optional[str] = None
    health_data: Dict[str, Any] = field(default_factory=dict)
    registry_key: Optional[str] = None
    registry_data: Dict[str, Any] = field(default_factory=dict)
    heartbeat_timestamp: Optional[datetime] = None
    module_type: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)


@dataclass
class CMSServiceData:
    """Service data from CMS sources."""
    service_definition: Dict[str, Any] = field(default_factory=dict)
    canonical_config: Dict[str, Any] = field(default_factory=dict)
    compliance_policies: List[Dict[str, Any]] = field(default_factory=list)
    expected_status: ServiceStatus = ServiceStatus.HEALTHY


@dataclass
class PrometheusServiceData:
    """Service data from Prometheus sources."""
    target_info: Dict[str, Any] = field(default_factory=dict)
    health_status: ServiceStatus = ServiceStatus.UNKNOWN
    metrics: Dict[str, float] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    last_scrape: Optional[datetime] = None


@dataclass
class GrafanaServiceData:
    """Service data from Grafana sources."""
    dashboard_links: List[str] = field(default_factory=list)
    alert_status: List[Dict[str, Any]] = field(default_factory=list)
    panel_queries: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class SpecServiceData:
    """Service data from specification sources."""
    required_by_spec: bool = False
    dag_dependencies: List[str] = field(default_factory=list)
    critical_path: bool = False
    architectural_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertStatus:
    """Alert status information."""
    alert_name: str
    status: str  # firing, pending, resolved
    severity: str
    description: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    started_at: Optional[datetime] = None


@dataclass
class ConfigurationChange:
    """Configuration change record."""
    timestamp: datetime
    field_name: str
    old_value: Any
    new_value: Any
    source: str  # redis, cms, prometheus, grafana, spec
    change_reason: Optional[str] = None


@dataclass
class ServiceEvent:
    """Service lifecycle event."""
    timestamp: datetime
    event_type: EventType
    service_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    source: str = "runtime_state_registry"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DriftDetection:
    """Configuration drift detection result."""
    service_name: str
    drift_type: DriftType
    severity: DriftSeverity
    source_layer: str  # spec, cms, runtime
    target_layer: str
    expected_value: Any
    actual_value: Any
    remediation_guidance: str
    auto_remediable: bool = False
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConfigurationDrift:
    """Configuration drift record for Phase 2 system."""
    service_name: str
    drift_type: str
    severity: DriftSeverity
    description: str
    expected_value: Any
    actual_value: Any
    remediation_suggestion: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "service_name": self.service_name,
            "drift_type": self.drift_type,
            "severity": self.severity.value,
            "description": self.description,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "remediation_suggestion": self.remediation_suggestion,
            "detected_at": self.detected_at.isoformat()
        }


@dataclass
class RemediationAction:
    """Auto-remediation action record."""
    service_name: str
    drift_detection: DriftDetection
    action_type: str  # restart, reconfigure, alert
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_details: Dict[str, Any] = field(default_factory=dict)
    executed_at: Optional[datetime] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None


@dataclass
class ComplianceScore:
    """Compliance scoring information."""
    overall_score: float  # 0.0-1.0
    spec_compliance: float
    cms_compliance: float
    service_scores: Dict[str, float] = field(default_factory=dict)
    trend: ComplianceTrend = ComplianceTrend.STABLE
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftSummary:
    """Summary of configuration drift."""
    total_services: int
    compliant_services: int
    drift_count_by_severity: Dict[DriftSeverity, int] = field(default_factory=dict)
    drift_count_by_type: Dict[DriftType, int] = field(default_factory=dict)
    auto_remediable_count: int = 0
    manual_intervention_count: int = 0


@dataclass
class UnifiedServiceState:
    """Unified service state from all sources."""
    service_name: str
    host: str
    port: int
    
    # Multi-source status information
    runtime_status: ServiceStatus = ServiceStatus.UNKNOWN
    cms_status: CMSStatus = CMSStatus.MISSING
    spec_status: SpecStatus = SpecStatus.UNSPECIFIED
    
    # State reconciliation
    compliance_score: float = 0.0
    drift_detections: List[DriftDetection] = field(default_factory=list)
    
    # Multi-source data
    redis_data: Optional[RedisServiceData] = None
    cms_data: Optional[CMSServiceData] = None
    prometheus_data: Optional[PrometheusServiceData] = None
    grafana_data: Optional[GrafanaServiceData] = None
    spec_data: Optional[SpecServiceData] = None
    
    # Observability integration
    grafana_dashboards: List[str] = field(default_factory=list)
    prometheus_queries: List[str] = field(default_factory=list)
    alert_status: List[AlertStatus] = field(default_factory=list)
    
    # Historical tracking
    last_seen: datetime = field(default_factory=datetime.utcnow)
    configuration_history: List[ConfigurationChange] = field(default_factory=list)
    lifecycle_events: List[ServiceEvent] = field(default_factory=list)


@dataclass
class SpecState:
    """What SHOULD be running according to specifications."""
    required_services: List[str] = field(default_factory=list)
    service_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    critical_path_services: List[str] = field(default_factory=list)
    architectural_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CMSState:
    """HOW services should be configured according to CMS."""
    service_definitions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    canonical_configurations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    compliance_policies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RuntimeState:
    """What IS actually running according to Redis/Prometheus/Grafana."""
    active_services: Dict[str, UnifiedServiceState] = field(default_factory=dict)
    health_summary: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    alert_summary: Dict[str, List[AlertStatus]] = field(default_factory=dict)


@dataclass
class ThreeLayerState:
    """Represents the three-layer state reconciliation."""
    spec_state: SpecState = field(default_factory=SpecState)
    cms_state: CMSState = field(default_factory=CMSState)
    runtime_state: RuntimeState = field(default_factory=RuntimeState)
    
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.IN_PROGRESS
    drift_summary: DriftSummary = field(default_factory=DriftSummary)
    compliance_score: ComplianceScore = field(default_factory=ComplianceScore)
    remediation_actions: List[RemediationAction] = field(default_factory=list)
    
    last_reconciliation: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HistoricalStateEvent:
    """Historical state change event."""
    timestamp: datetime
    event_type: EventType
    service_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    source: str = "runtime_state_registry"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class QueryResult:
    """Result of a state query."""
    query: str
    result_type: str  # service_list, service_detail, health_summary, etc.
    data: Any
    source_attribution: Dict[str, str] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    from_context: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """Result of context validation against runtime state."""
    valid: bool
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    context_freshness: Dict[str, datetime] = field(default_factory=dict)

# Additional models for Grafana Intelligence Collector

class HealthStatus(Enum):
    """Health status enumeration for monitoring."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class DashboardInfo:
    """Information about a Grafana dashboard."""
    name: str
    url: str
    panels_count: int
    last_updated: datetime


@dataclass
class AlertState:
    """State of a monitoring alert."""
    name: str
    status: str  # ok, pending, alerting, no_data
    severity: str
    message: str
    last_triggered: datetime


@dataclass
class MonitoringState:
    """Comprehensive monitoring state for a service."""
    service_name: str
    dashboards: List[DashboardInfo] = field(default_factory=list)
    alerts: List[AlertState] = field(default_factory=list)
    health_status: HealthStatus = HealthStatus.UNKNOWN
    metrics_available: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConfigurationState:
    """Configuration state information."""
    service_name: str
    current_config: Dict[str, Any] = field(default_factory=dict)
    canonical_config: Dict[str, Any] = field(default_factory=dict)
    drift_detected: bool = False
    last_validated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceState:
    """Complete service state information."""
    service_name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.UNKNOWN
    health_status: HealthStatus = HealthStatus.UNKNOWN
    configuration: Optional[ConfigurationState] = None
    monitoring: Optional[MonitoringState] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)