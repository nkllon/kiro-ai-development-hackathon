"""
Data models for the Anti-Duplication System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class OverlapRecommendation(Enum):
    """Recommendation for handling capability overlap."""
    BLOCK = "block"  # Block development due to high overlap
    ENHANCE = "enhance"  # Enhance existing capability instead
    PROCEED = "proceed"  # Proceed with new development
    REVIEW = "review"  # Requires manual review


class CapabilityType(Enum):
    """Types of capabilities that can be discovered."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SERVICE = "service"
    API_ENDPOINT = "api_endpoint"
    SCRIPT = "script"
    FRAMEWORK = "framework"


@dataclass
class ExistingSolution:
    """Represents an existing solution found in the codebase."""
    solution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    file_path: str = ""
    capability_type: CapabilityType = CapabilityType.FUNCTION
    functionality_summary: str = ""
    usage_examples: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    last_modified: Optional[datetime] = None
    maintainer: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class CapabilityGap:
    """Represents a gap in existing capabilities."""
    gap_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    required_functionality: str = ""
    priority: str = "medium"  # low, medium, high, critical
    estimated_effort: str = ""  # hours, days, weeks
    potential_solutions: List[str] = field(default_factory=list)


@dataclass
class EnhancementOpportunity:
    """Represents an opportunity to enhance existing capabilities."""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    existing_solution_id: str = ""
    enhancement_description: str = ""
    estimated_effort: str = ""
    value_proposition: str = ""
    risk_assessment: str = ""


@dataclass
class CapabilityInventory:
    """Complete inventory of capabilities for a problem domain."""
    domain: str = ""
    existing_solutions: List[ExistingSolution] = field(default_factory=list)
    capability_gaps: List[CapabilityGap] = field(default_factory=list)
    enhancement_opportunities: List[EnhancementOpportunity] = field(default_factory=list)
    discovery_timestamp: datetime = field(default_factory=datetime.utcnow)
    discovery_completeness_score: float = 0.0  # 0.0-1.0
    total_capabilities_found: int = 0
    
    @property
    def has_existing_solutions(self) -> bool:
        """Check if any existing solutions were found."""
        return len(self.existing_solutions) > 0
    
    @property
    def enhancement_recommended(self) -> bool:
        """Check if enhancement is recommended over new development."""
        return len(self.enhancement_opportunities) > 0


@dataclass
class OverlappingCapability:
    """Represents a capability that overlaps with proposed development."""
    existing_solution: ExistingSolution
    similarity_score: float  # 0.0-1.0
    overlap_description: str = ""
    functional_differences: List[str] = field(default_factory=list)
    enhancement_potential: bool = False


@dataclass
class OverlapAnalysis:
    """Analysis of functional overlap between proposed and existing capabilities."""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    functional_similarity_score: float = 0.0  # 0.0-1.0
    overlapping_capabilities: List[OverlappingCapability] = field(default_factory=list)
    unique_value_proposition: Optional[str] = None
    recommendation: OverlapRecommendation = OverlapRecommendation.REVIEW
    justification_required: bool = True
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def has_significant_overlap(self) -> bool:
        """Check if there is significant functional overlap (>70%)."""
        return self.functional_similarity_score > 0.7
    
    @property
    def should_block_development(self) -> bool:
        """Check if development should be blocked due to overlap."""
        return self.recommendation == OverlapRecommendation.BLOCK


@dataclass
class DiscoveryAttestation:
    """Cryptographically signed attestation of completed discovery."""
    attestation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_domain: str = ""
    discovery_completeness_score: float = 0.0
    existing_solutions_found: int = 0
    overlap_analysis_completed: bool = False
    enhancement_vs_new_justified: bool = False
    justification_text: str = ""
    attestation_signature: str = ""  # Cryptographic proof
    attestation_timestamp: datetime = field(default_factory=datetime.utcnow)
    attesting_agent: str = ""  # Who/what created this attestation
    
    @property
    def is_valid(self) -> bool:
        """Check if attestation is valid for proceeding with development."""
        return (
            self.discovery_completeness_score >= 0.8 and
            self.overlap_analysis_completed and
            (not self.existing_solutions_found or self.enhancement_vs_new_justified) and
            self.attestation_signature != ""
        )


@dataclass
class DevelopmentRequest:
    """Represents a request for new development."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_statement: str = ""
    proposed_solution: str = ""
    requester: str = ""
    priority: str = "medium"
    estimated_effort: str = ""
    success_criteria: List[str] = field(default_factory=list)
    request_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Discovery tracking
    discovery_completed: bool = False
    discovery_attestation_id: Optional[str] = None
    development_approved: bool = False
    approval_timestamp: Optional[datetime] = None


@dataclass
class GateDecision:
    """Decision made by the development gate."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    decision: str = ""  # APPROVED, BLOCKED, REVIEW_REQUIRED
    reasoning: str = ""
    required_actions: List[str] = field(default_factory=list)
    decision_timestamp: datetime = field(default_factory=datetime.utcnow)
    decision_maker: str = ""  # System or human reviewer
    
    @property
    def is_approved(self) -> bool:
        """Check if development is approved to proceed."""
        return self.decision == "APPROVED"
    
    @property
    def is_blocked(self) -> bool:
        """Check if development is blocked."""
        return self.decision == "BLOCKED"


@dataclass
class AuditLogEntry:
    """Entry in the audit log for compliance tracking."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""  # DISCOVERY_COMPLETED, DEVELOPMENT_BLOCKED, etc.
    request_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    actor: str = ""  # Who performed the action
    integrity_hash: str = ""  # For tamper detection
    
    def __post_init__(self):
        """Calculate integrity hash after initialization."""
        if not self.integrity_hash:
            import hashlib
            import json
            
            data = {
                "entry_id": self.entry_id,
                "timestamp": self.timestamp.isoformat(),
                "event_type": self.event_type,
                "request_id": self.request_id,
                "details": self.details,
                "actor": self.actor
            }
            
            data_str = json.dumps(data, sort_keys=True)
            self.integrity_hash = hashlib.sha256(data_str.encode()).hexdigest()