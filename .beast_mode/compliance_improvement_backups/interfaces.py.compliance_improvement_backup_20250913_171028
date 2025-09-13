"""Core interfaces for the Visual Diagram Quality Validation Pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import PNGImage, AnalysisResult, QualityViolation, Recommendation


class ProcessorInterface(ABC):
    """Base interface for format-specific processors."""
    
    @abstractmethod
    def can_process(self, input_data: bytes, filename: Optional[str] = None) -> bool:
        """Check if this processor can handle the input format."""
        pass
    
    @abstractmethod
    def render_to_png(self, input_data: bytes, width: int = 2048, height: int = 2048, 
                     dpi: int = 300) -> PNGImage:
        """Convert input to standardized PNG format."""
        pass
    
    @abstractmethod
    def extract_metadata(self, input_data: bytes) -> Dict[str, Any]:
        """Extract format-specific metadata from input."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of file extensions this processor supports."""
        pass


class QualityAnalyzer(ABC):
    """Base interface for quality analysis modules."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize analyzer with optional configuration."""
        self.config = config or {}
    
    @abstractmethod
    def analyze(self, image: PNGImage, metadata: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Analyze image for quality violations and generate recommendations."""
        pass
    
    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """Name of this analyzer."""
        pass
    
    @property
    @abstractmethod
    def supported_rules(self) -> List[str]:
        """List of quality rules this analyzer enforces."""
        pass
    
    def is_enabled(self, rule_id: str) -> bool:
        """Check if a specific rule is enabled in configuration."""
        return self.config.get(f"enable_{rule_id}", True)
    
    def get_threshold(self, rule_id: str, default: float) -> float:
        """Get threshold value for a rule from configuration."""
        return self.config.get(f"{rule_id}_threshold", default)


class FeedbackGenerator(ABC):
    """Interface for generating user-friendly feedback from analysis results."""
    
    @abstractmethod
    def generate_report(self, analysis_results: List[AnalysisResult], 
                       audience_mode: str = "general") -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        pass
    
    @abstractmethod
    def format_recommendations(self, recommendations: List[Recommendation], 
                             audience_mode: str = "general") -> List[str]:
        """Format recommendations for specific audience."""
        pass
    
    @abstractmethod
    def create_visual_annotations(self, violations: List[QualityViolation], 
                                image: PNGImage) -> PNGImage:
        """Create annotated image highlighting violations."""
        pass


class ValidationPipeline(ABC):
    """Main pipeline interface for orchestrating validation."""
    
    @abstractmethod
    def validate(self, input_data: bytes, filename: Optional[str] = None,
                audience_mode: str = "general") -> Dict[str, Any]:
        """Run complete validation pipeline on input."""
        pass
    
    @abstractmethod
    def add_analyzer(self, analyzer: QualityAnalyzer) -> None:
        """Add a quality analyzer to the pipeline."""
        pass
    
    @abstractmethod
    def add_processor(self, processor: ProcessorInterface) -> None:
        """Add a format processor to the pipeline."""
        pass