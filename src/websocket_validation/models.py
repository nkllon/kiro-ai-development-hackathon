"""
Core data models and types for WebSocket validation framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


class ValidationStatus(Enum):
    """Overall validation execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class TestStatus(Enum):
    """Individual test execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class EvidenceType(Enum):
    """Types of evidence that can be collected."""
    LOG_FILE = "log_file"
    NETWORK_CAPTURE = "network_capture"
    SCREENSHOT = "screenshot"
    CONFIG_SNAPSHOT = "config_snapshot"
    TEST_OUTPUT = "test_output"
    HTTP_RESPONSE = "http_response"
    WEBSOCKET_TRACE = "websocket_trace"
    CODE_ANALYSIS = "code_analysis"
    PERFORMANCE_METRICS = "performance_metrics"


class GapAssessmentResult(Enum):
    """Overall assessment of implementation gap claims."""
    CLAIMS_VALIDATED = "claims_validated"  # Gap analysis claims are accurate
    CLAIMS_REFUTED = "claims_refuted"      # Gap analysis claims are false
    MIXED_RESULTS = "mixed_results"        # Some claims valid, some invalid
    INCONCLUSIVE = "inconclusive"          # Insufficient evidence


class ErrorType(Enum):
    """Types of validation errors."""
    NETWORK_ERROR = "network_error"
    CONFIG_ERROR = "config_error"
    CODE_ANALYSIS_ERROR = "code_analysis_error"
    SYSTEM_ERROR = "system_error"
    EVIDENCE_ERROR = "evidence_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"


@dataclass
class Evidence:
    """Evidence collected during validation."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    evidence_type: EvidenceType = EvidenceType.TEST_OUTPUT
    source_test: str = ""
    data: Union[bytes, str, Dict] = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: str = ""
    file_path: Optional[str] = None
    
    def __post_init__(self):
        """Calculate integrity hash after initialization."""
        if not self.integrity_hash and self.data:
            import hashlib
            if isinstance(self.data, str):
                data_bytes = self.data.encode('utf-8')
            elif isinstance(self.data, dict):
                import json
                data_bytes = json.dumps(self.data, sort_keys=True).encode('utf-8')
            else:
                data_bytes = self.data
            
            self.integrity_hash = hashlib.sha256(data_bytes).hexdigest()


@dataclass
class TestResult:
    """Result of an individual test execution."""
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_name: str = ""
    test_category: str = ""
    status: TestStatus = TestStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    evidence_ids: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0
    
    @property
    def duration(self) -> float:
        """Calculate test duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return self.execution_time
    
    @property
    def success_rate(self) -> float:
        """Calculate test success rate as percentage."""
        total_assertions = self.assertions_passed + self.assertions_failed
        if total_assertions == 0:
            return 100.0 if self.status == TestStatus.PASSED else 0.0
        return (self.assertions_passed / total_assertions) * 100.0


@dataclass
class EndpointResult:
    """Result of testing a specific endpoint."""
    url: str = ""
    method: str = "GET"
    status_code: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    response_time: float = 0.0
    response_body: str = ""
    websocket_upgrade_success: bool = False
    websocket_protocol: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_success(self) -> bool:
        """Check if endpoint test was successful."""
        return 200 <= self.status_code < 300 or (
            self.status_code == 101 and self.websocket_upgrade_success
        )
    
    @property
    def is_websocket_upgrade(self) -> bool:
        """Check if response indicates WebSocket upgrade."""
        return (
            self.status_code == 101 and
            self.headers.get("upgrade", "").lower() == "websocket" and
            "websocket" in self.headers.get("connection", "").lower()
        )


@dataclass
class HandshakeResult:
    """Result of WebSocket handshake testing."""
    endpoint_url: str = ""
    handshake_success: bool = False
    upgrade_header: Optional[str] = None
    connection_header: Optional[str] = None
    websocket_accept: Optional[str] = None
    websocket_protocol: Optional[str] = None
    error_message: Optional[str] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StabilityResult:
    """Result of connection stability testing."""
    endpoint_url: str = ""
    connection_duration: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0
    connection_drops: int = 0
    average_latency: float = 0.0
    max_latency: float = 0.0
    min_latency: float = 0.0
    error_count: int = 0
    success_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RouteAnalysis:
    """Result of FastAPI route analysis."""
    total_routes: int = 0
    websocket_routes: List[str] = field(default_factory=list)
    http_routes: List[str] = field(default_factory=list)
    route_handlers: Dict[str, str] = field(default_factory=dict)
    middleware_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HandlerAnalysis:
    """Result of WebSocket handler analysis."""
    handler_name: str = ""
    has_accept_logic: bool = False
    has_receive_logic: bool = False
    has_send_logic: bool = False
    has_error_handling: bool = False
    imports_websocket: bool = False
    complexity_score: int = 0
    line_count: int = 0
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DependencyAnalysis:
    """Result of dependency analysis."""
    required_packages: List[str] = field(default_factory=list)
    installed_packages: List[str] = field(default_factory=list)
    missing_packages: List[str] = field(default_factory=list)
    version_conflicts: List[str] = field(default_factory=list)
    websocket_libraries: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompletenessAnalysis:
    """Result of implementation completeness analysis."""
    total_features: int = 0
    implemented_features: int = 0
    missing_features: List[str] = field(default_factory=list)
    partial_features: List[str] = field(default_factory=list)
    completeness_percentage: float = 0.0
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GapAssessment:
    """Assessment of implementation gap claims."""
    claims_validated: int = 0
    claims_refuted: int = 0
    claims_inconclusive: int = 0
    documentation_accuracy_percentage: float = 0.0
    implementation_completeness_percentage: float = 0.0
    overall_assessment: GapAssessmentResult = GapAssessmentResult.INCONCLUSIVE
    supporting_evidence: List[str] = field(default_factory=list)
    refuting_evidence: List[str] = field(default_factory=list)
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_claims(self) -> int:
        """Total number of claims assessed."""
        return self.claims_validated + self.claims_refuted + self.claims_inconclusive
    
    @property
    def validation_confidence(self) -> float:
        """Confidence level in validation results (0-100)."""
        if self.total_claims == 0:
            return 0.0
        decisive_claims = self.claims_validated + self.claims_refuted
        return (decisive_claims / self.total_claims) * 100.0


@dataclass
class Recommendation:
    """Actionable recommendation based on validation results."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: str = "medium"  # low, medium, high, critical
    category: str = ""  # implementation, configuration, documentation, etc.
    action_items: List[str] = field(default_factory=list)
    evidence_references: List[str] = field(default_factory=list)
    estimated_effort: str = ""  # hours, days, weeks
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvidenceSummary:
    """Summary of collected evidence."""
    total_evidence_items: int = 0
    evidence_by_type: Dict[str, int] = field(default_factory=dict)
    evidence_by_test: Dict[str, int] = field(default_factory=dict)
    total_size_bytes: int = 0
    integrity_verified: bool = True
    collection_start: Optional[datetime] = None
    collection_end: Optional[datetime] = None


@dataclass
class ValidationReport:
    """Complete validation report."""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    overall_status: ValidationStatus = ValidationStatus.NOT_STARTED
    test_results: List[TestResult] = field(default_factory=list)
    evidence_summary: EvidenceSummary = field(default_factory=EvidenceSummary)
    gap_assessment: GapAssessment = field(default_factory=GapAssessment)
    recommendations: List[Recommendation] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    execution_duration: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Overall success rate of all tests."""
        if not self.test_results:
            return 0.0
        
        passed_tests = sum(1 for test in self.test_results if test.status == TestStatus.PASSED)
        return (passed_tests / len(self.test_results)) * 100.0
    
    @property
    def total_tests(self) -> int:
        """Total number of tests executed."""
        return len(self.test_results)
    
    @property
    def failed_tests(self) -> List[TestResult]:
        """List of failed tests."""
        return [test for test in self.test_results if test.status == TestStatus.FAILED]
    
    @property
    def passed_tests(self) -> List[TestResult]:
        """List of passed tests."""
        return [test for test in self.test_results if test.status == TestStatus.PASSED]