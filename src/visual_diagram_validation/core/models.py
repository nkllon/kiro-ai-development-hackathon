"""Core data models for the Visual Diagram Quality Validation Pipeline."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class Severity(Enum):
    """Violation severity levels."""
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"


class ActionType(Enum):
    """Recommendation action types."""
    INCREASE = "increase"
    DECREASE = "decrease"
    CHANGE = "change"
    ADD = "add"
    REMOVE = "remove"


@dataclass
class BoundingBox:
    """Represents a rectangular region in the image."""
    x: int
    y: int
    width: int
    height: int
    
    def center(self) -> Tuple[int, int]:
        """Get the center point of the bounding box."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def area(self) -> int:
        """Calculate the area of the bounding box."""
        return self.width * self.height


@dataclass
class PNGImage:
    """Represents a processed PNG image with metadata."""
    data: bytes
    width: int
    height: int
    dpi: int
    color_mode: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def aspect_ratio(self) -> float:
        """Calculate the aspect ratio of the image."""
        return self.width / self.height if self.height > 0 else 0.0
    
    def size_mb(self) -> float:
        """Get the size of the image data in megabytes."""
        return len(self.data) / (1024 * 1024)


@dataclass
class QualityViolation:
    """Represents a quality rule violation found in the diagram."""
    rule_id: str
    severity: Severity
    location: Optional[BoundingBox]
    current_value: float
    expected_value: float
    description: str
    category: str = "general"
    
    def __post_init__(self):
        """Ensure severity is a Severity enum."""
        if isinstance(self.severity, str):
            self.severity = Severity(self.severity)


@dataclass
class Recommendation:
    """Represents an actionable recommendation to fix a violation."""
    violation_id: str
    action_type: ActionType
    specific_guidance: str
    expected_outcome: str
    priority: int = 1  # 1=high, 2=medium, 3=low
    
    def __post_init__(self):
        """Ensure action_type is an ActionType enum."""
        if isinstance(self.action_type, str):
            self.action_type = ActionType(self.action_type)


@dataclass
class AnalysisResult:
    """Results from a quality analyzer."""
    analyzer_name: str
    violations: List[QualityViolation]
    recommendations: List[Recommendation]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_errors(self) -> bool:
        """Check if any violations are errors."""
        return any(v.severity == Severity.ERROR for v in self.violations)
    
    def has_warnings(self) -> bool:
        """Check if any violations are warnings."""
        return any(v.severity == Severity.WARNING for v in self.violations)


@dataclass
class QualityReport:
    """Comprehensive quality report for a diagram."""
    overall_score: float  # 0-100 scale
    violations: List[QualityViolation]
    recommendations: List[Recommendation]
    processing_time: float
    audience_mode: str
    analysis_results: List[AnalysisResult] = field(default_factory=list)
    
    def error_count(self) -> int:
        """Count of error-level violations."""
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)
    
    def warning_count(self) -> int:
        """Count of warning-level violations."""
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)
    
    def is_passing(self, min_score: float = 70.0) -> bool:
        """Check if the diagram passes quality standards."""
        return self.overall_score >= min_score and self.error_count() == 0