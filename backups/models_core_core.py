"""
Models Core Core

This module was extracted from models_core.py
as part of RM-DDD compliance refactoring.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import uuid

class FindingType(Enum):
    """Types of findings that expert agents can detect"""
    SYNTAX_ERROR = 'syntax_error'
    SECURITY_VULNERABILITY = 'security_vulnerability'
    PERFORMANCE_ISSUE = 'performance_issue'
    ARCHITECTURE_VIOLATION = 'architecture_violation'
    QUALITY_ISSUE = 'quality_issue'
    BUILD_FAILURE = 'build_failure'
    DEPENDENCY_ISSUE = 'dependency_issue'

class Severity(Enum):
    """Severity levels for findings and delusions"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INFO = 'info'

class DelusionCategory(Enum):
    """Categories of systematic delusions that can be detected"""
    SYNTAX = 'syntax'
    SECURITY = 'security'
    ARCHITECTURE = 'architecture'
    QUALITY = 'quality'
    PERFORMANCE = 'performance'
    BUILD = 'build'

class RecoveryComplexity(Enum):
    """Complexity levels for recovery operations"""
    TRIVIAL = 'trivial'
    SIMPLE = 'simple'
    MODERATE = 'moderate'
    COMPLEX = 'complex'
    CRITICAL = 'critical'

@dataclass
class CodeLocation:
    """Represents a location in source code"""
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self) -> str:
        if self.column_number:
            return f'{self.file_path}:{self.line_number}:{self.column_number}'
        return f'{self.file_path}:{self.line_number}'

@dataclass
class Finding:
    """Represents a finding from expert agent analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: FindingType = FindingType.QUALITY_ISSUE
    severity: Severity = Severity.MEDIUM
    location: Optional[CodeLocation] = None
    description: str = ''
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate finding data"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
        if not self.description.strip():
            raise ValueError('Finding description cannot be empty')

@dataclass
class Recommendation:
    """Represents a recommendation from expert agent analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ''
    description: str = ''
    priority: Severity = Severity.MEDIUM
    effort_estimate: str = ''
    automated_fix_available: bool = False
    fix_command: Optional[str] = None
    related_findings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate recommendation data"""
        if not self.title.strip():
            raise ValueError('Recommendation title cannot be empty')
        if not self.description.strip():
            raise ValueError('Recommendation description cannot be empty')

@dataclass
class AnalysisContext:
    """Context information for expert agent analysis"""
    target_path: str
    analysis_type: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate analysis context"""
        if not self.target_path.strip():
            raise ValueError('Target path cannot be empty')
        if not self.analysis_type.strip():
            raise ValueError('Analysis type cannot be empty')

@dataclass
class AnalysisResult:
    """Result from expert agent analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ''
    confidence: float = 0.0
    findings: List[Finding] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_duration: float = 0.0
    context: Optional[AnalysisContext] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate analysis result"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
        if not self.agent_name.strip():
            raise ValueError('Agent name cannot be empty')
        if self.analysis_duration < 0:
            raise ValueError('Analysis duration cannot be negative')

    def get_critical_findings(self) -> List[Finding]:
        """Get all critical severity findings"""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    def get_high_confidence_findings(self, threshold: float=0.8) -> List[Finding]:
        """Get findings above confidence threshold"""
        return [f for f in self.findings if f.confidence >= threshold]

@dataclass
class Delusion:
    """Represents a systematic delusion detected in code"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: DelusionCategory = DelusionCategory.QUALITY
    pattern: str = ''
    severity: Severity = Severity.MEDIUM
    recovery_complexity: RecoveryComplexity = RecoveryComplexity.MODERATE
    location: Optional[CodeLocation] = None
    description: str = ''
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate delusion data"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
        if not self.pattern.strip():
            raise ValueError('Delusion pattern cannot be empty')
        if not self.description.strip():
            raise ValueError('Delusion description cannot be empty')

@dataclass
class RecoveryAction:
    """Represents a single recovery action"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ''
    target: str = ''
    content: str = ''
    validation_required: bool = True
    rollback_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryPlan:
    """Plan for recovering from detected delusions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    delusion_id: str = ''
    actions: List[RecoveryAction] = field(default_factory=list)
    estimated_duration: float = 0.0
    risk_level: Severity = Severity.MEDIUM
    requires_human_approval: bool = False
    rollback_plan: List[RecoveryAction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate recovery plan"""
        if not self.delusion_id.strip():
            raise ValueError('Delusion ID cannot be empty')
        if not self.actions:
            raise ValueError('Recovery plan must have at least one action')
        if self.estimated_duration < 0:
            raise ValueError('Estimated duration cannot be negative')

@dataclass
class ValidationResult:
    """Result from validation operations"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    validation_type: str = ''
    success: bool = False
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate validation result"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
        if not self.validation_type.strip():
            raise ValueError('Validation type cannot be empty')
        if self.validation_duration < 0:
            raise ValueError('Validation duration cannot be negative')

@dataclass
class ConsensusResult:
    """Result from multi-agent consensus building"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    consensus_reached: bool = False
    confidence: float = 0.0
    unified_result: Optional[AnalysisResult] = None
    participating_agents: List[str] = field(default_factory=list)
    dissenting_opinions: List[AnalysisResult] = field(default_factory=list)
    resolution_method: str = ''
    consensus_duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate consensus result"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
        if self.consensus_reached and (not self.unified_result):
            raise ValueError('Unified result required when consensus is reached')
        if not self.participating_agents:
            raise ValueError('At least one participating agent required')
        if self.consensus_duration < 0:
            raise ValueError('Consensus duration cannot be negative')

@dataclass
class ValidationCertificate:
    """Certificate issued after successful validation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target: str = ''
    validation_results: List[ValidationResult] = field(default_factory=list)
    overall_confidence: float = 0.0
    certificate_level: str = ''
    valid_until: Optional[datetime] = None
    issued_at: datetime = field(default_factory=datetime.utcnow)
    issuer: str = 'Ghostbusters Framework'

    def __post_init__(self):
        """Validate certificate data"""
        if not 0.0 <= self.overall_confidence <= 1.0:
            raise ValueError(f'Overall confidence must be between 0.0 and 1.0, got {self.overall_confidence}')
        if not self.target.strip():
            raise ValueError('Certificate target cannot be empty')
        if not self.validation_results:
            raise ValueError('Certificate must have at least one validation result')

@dataclass
class MultiDimensionalResult:
    """Result from multi-dimensional smoke testing"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    functional_score: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    integration_score: float = 0.0
    overall_confidence: float = 0.0
    validation_certificate: Optional[ValidationCertificate] = None
    detailed_results: Dict[str, ValidationResult] = field(default_factory=dict)
    test_duration: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate multi-dimensional result"""
        scores = [self.functional_score, self.performance_score, self.security_score, self.integration_score, self.overall_confidence]
        for score in scores:
            if not 0.0 <= score <= 1.0:
                raise ValueError(f'All scores must be between 0.0 and 1.0, got {score}')
        if self.test_duration < 0:
            raise ValueError('Test duration cannot be negative')

    def get_failing_dimensions(self, threshold: float=0.7) -> List[str]:
        """Get dimensions that failed to meet threshold"""
        failing = []
        if self.functional_score < threshold:
            failing.append('functional')
        if self.performance_score < threshold:
            failing.append('performance')
        if self.security_score < threshold:
            failing.append('security')
        if self.integration_score < threshold:
            failing.append('integration')
        return failing

    def is_production_ready(self, threshold: float=0.8) -> bool:
        """Check if all dimensions meet production readiness threshold"""
        return all((score >= threshold for score in [self.functional_score, self.performance_score, self.security_score, self.integration_score]))

def __str__(self) -> str:
    if self.column_number:
        return f'{self.file_path}:{self.line_number}:{self.column_number}'
    return f'{self.file_path}:{self.line_number}'

def __post_init__(self):
    """Validate finding data"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.description.strip():
        raise ValueError('Finding description cannot be empty')

def __post_init__(self):
    """Validate recommendation data"""
    if not self.title.strip():
        raise ValueError('Recommendation title cannot be empty')
    if not self.description.strip():
        raise ValueError('Recommendation description cannot be empty')

def __post_init__(self):
    """Validate analysis context"""
    if not self.target_path.strip():
        raise ValueError('Target path cannot be empty')
    if not self.analysis_type.strip():
        raise ValueError('Analysis type cannot be empty')

def __post_init__(self):
    """Validate analysis result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.agent_name.strip():
        raise ValueError('Agent name cannot be empty')
    if self.analysis_duration < 0:
        raise ValueError('Analysis duration cannot be negative')

def get_critical_findings(self) -> List[Finding]:
    """Get all critical severity findings"""
    return [f for f in self.findings if f.severity == Severity.CRITICAL]

def get_high_confidence_findings(self, threshold: float=0.8) -> List[Finding]:
    """Get findings above confidence threshold"""
    return [f for f in self.findings if f.confidence >= threshold]

def __post_init__(self):
    """Validate delusion data"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.pattern.strip():
        raise ValueError('Delusion pattern cannot be empty')
    if not self.description.strip():
        raise ValueError('Delusion description cannot be empty')

def __post_init__(self):
    """Validate recovery plan"""
    if not self.delusion_id.strip():
        raise ValueError('Delusion ID cannot be empty')
    if not self.actions:
        raise ValueError('Recovery plan must have at least one action')
    if self.estimated_duration < 0:
        raise ValueError('Estimated duration cannot be negative')

def __post_init__(self):
    """Validate validation result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.validation_type.strip():
        raise ValueError('Validation type cannot be empty')
    if self.validation_duration < 0:
        raise ValueError('Validation duration cannot be negative')

def __post_init__(self):
    """Validate consensus result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if self.consensus_reached and (not self.unified_result):
        raise ValueError('Unified result required when consensus is reached')
    if not self.participating_agents:
        raise ValueError('At least one participating agent required')
    if self.consensus_duration < 0:
        raise ValueError('Consensus duration cannot be negative')

def __post_init__(self):
    """Validate certificate data"""
    if not 0.0 <= self.overall_confidence <= 1.0:
        raise ValueError(f'Overall confidence must be between 0.0 and 1.0, got {self.overall_confidence}')
    if not self.target.strip():
        raise ValueError('Certificate target cannot be empty')
    if not self.validation_results:
        raise ValueError('Certificate must have at least one validation result')

def __post_init__(self):
    """Validate multi-dimensional result"""
    scores = [self.functional_score, self.performance_score, self.security_score, self.integration_score, self.overall_confidence]
    for score in scores:
        if not 0.0 <= score <= 1.0:
            raise ValueError(f'All scores must be between 0.0 and 1.0, got {score}')
    if self.test_duration < 0:
        raise ValueError('Test duration cannot be negative')

def get_failing_dimensions(self, threshold: float=0.7) -> List[str]:
    """Get dimensions that failed to meet threshold"""
    failing = []
    if self.functional_score < threshold:
        failing.append('functional')
    if self.performance_score < threshold:
        failing.append('performance')
    if self.security_score < threshold:
        failing.append('security')
    if self.integration_score < threshold:
        failing.append('integration')
    return failing

def is_production_ready(self, threshold: float=0.8) -> bool:
    """Check if all dimensions meet production readiness threshold"""
    return all((score >= threshold for score in [self.functional_score, self.performance_score, self.security_score, self.integration_score]))

def __str__(self) -> str:
    if self.column_number:
        return f'{self.file_path}:{self.line_number}:{self.column_number}'
    return f'{self.file_path}:{self.line_number}'

def __post_init__(self):
    """Validate finding data"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.description.strip():
        raise ValueError('Finding description cannot be empty')

def __post_init__(self):
    """Validate recommendation data"""
    if not self.title.strip():
        raise ValueError('Recommendation title cannot be empty')
    if not self.description.strip():
        raise ValueError('Recommendation description cannot be empty')

def __post_init__(self):
    """Validate analysis context"""
    if not self.target_path.strip():
        raise ValueError('Target path cannot be empty')
    if not self.analysis_type.strip():
        raise ValueError('Analysis type cannot be empty')

def __post_init__(self):
    """Validate analysis result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.agent_name.strip():
        raise ValueError('Agent name cannot be empty')
    if self.analysis_duration < 0:
        raise ValueError('Analysis duration cannot be negative')

def get_critical_findings(self) -> List[Finding]:
    """Get all critical severity findings"""
    return [f for f in self.findings if f.severity == Severity.CRITICAL]

def get_high_confidence_findings(self, threshold: float=0.8) -> List[Finding]:
    """Get findings above confidence threshold"""
    return [f for f in self.findings if f.confidence >= threshold]

def __post_init__(self):
    """Validate delusion data"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.pattern.strip():
        raise ValueError('Delusion pattern cannot be empty')
    if not self.description.strip():
        raise ValueError('Delusion description cannot be empty')

def __post_init__(self):
    """Validate recovery plan"""
    if not self.delusion_id.strip():
        raise ValueError('Delusion ID cannot be empty')
    if not self.actions:
        raise ValueError('Recovery plan must have at least one action')
    if self.estimated_duration < 0:
        raise ValueError('Estimated duration cannot be negative')

def __post_init__(self):
    """Validate validation result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if not self.validation_type.strip():
        raise ValueError('Validation type cannot be empty')
    if self.validation_duration < 0:
        raise ValueError('Validation duration cannot be negative')

def __post_init__(self):
    """Validate consensus result"""
    if not 0.0 <= self.confidence <= 1.0:
        raise ValueError(f'Confidence must be between 0.0 and 1.0, got {self.confidence}')
    if self.consensus_reached and (not self.unified_result):
        raise ValueError('Unified result required when consensus is reached')
    if not self.participating_agents:
        raise ValueError('At least one participating agent required')
    if self.consensus_duration < 0:
        raise ValueError('Consensus duration cannot be negative')

def __post_init__(self):
    """Validate certificate data"""
    if not 0.0 <= self.overall_confidence <= 1.0:
        raise ValueError(f'Overall confidence must be between 0.0 and 1.0, got {self.overall_confidence}')
    if not self.target.strip():
        raise ValueError('Certificate target cannot be empty')
    if not self.validation_results:
        raise ValueError('Certificate must have at least one validation result')

def __post_init__(self):
    """Validate multi-dimensional result"""
    scores = [self.functional_score, self.performance_score, self.security_score, self.integration_score, self.overall_confidence]
    for score in scores:
        if not 0.0 <= score <= 1.0:
            raise ValueError(f'All scores must be between 0.0 and 1.0, got {score}')
    if self.test_duration < 0:
        raise ValueError('Test duration cannot be negative')

def get_failing_dimensions(self, threshold: float=0.7) -> List[str]:
    """Get dimensions that failed to meet threshold"""
    failing = []
    if self.functional_score < threshold:
        failing.append('functional')
    if self.performance_score < threshold:
        failing.append('performance')
    if self.security_score < threshold:
        failing.append('security')
    if self.integration_score < threshold:
        failing.append('integration')
    return failing

def is_production_ready(self, threshold: float=0.8) -> bool:
    """Check if all dimensions meet production readiness threshold"""
    return all((score >= threshold for score in [self.functional_score, self.performance_score, self.security_score, self.integration_score]))
