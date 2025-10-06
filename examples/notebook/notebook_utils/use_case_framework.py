"""
Base framework for use case demonstrations.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class UseCaseResult:
    """Results from executing a use case demonstration."""
    use_case_name: str
    execution_time: float
    success: bool
    outputs: Dict[str, Any]
    metrics: Dict[str, float]
    visualizations: List[str]
    errors: List[str]
    recommendations: List[str]


class UseCase(ABC):
    """Base class for all use case demonstrations."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        
    def setup(self) -> None:
        """Setup demonstration environment."""
        print(f"🔧 Setting up {self.name}...")
        
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the use case demonstration."""
        pass
        
    def visualize(self, results: Dict[str, Any]) -> List[str]:
        """Create visualizations for the results."""
        print(f"📊 Creating visualizations for {self.name}...")
        return []
        
    def explain(self) -> str:
        """Provide detailed explanation of the use case."""
        return f"This demonstrates {self.name} functionality."
    
    def run_complete_demonstration(self) -> UseCaseResult:
        """Run the complete use case demonstration."""
        self.start_time = time.time()
        errors = []
        outputs = {}
        visualizations = []
        
        try:
            self.setup()
            outputs = self.execute()
            visualizations = self.visualize(outputs)
            success = True
        except Exception as e:
            errors.append(str(e))
            success = False
            
        execution_time = time.time() - self.start_time
        
        return UseCaseResult(
            use_case_name=self.name,
            execution_time=execution_time,
            success=success,
            outputs=outputs,
            metrics={'execution_time': execution_time},
            visualizations=visualizations,
            errors=errors,
            recommendations=[]
        )


class DimensionAnalysisUseCase(UseCase):
    """Demonstration of 22-dimension analysis."""
    
    def __init__(self):
        super().__init__("22-Dimension Analysis")
        
    def execute(self) -> Dict[str, Any]:
        """Execute dimension analysis demonstration."""
        import random
        
        dimensions = [
            'Functional Completeness', 'Technical Depth', 'Integration Clarity',
            'Error Handling', 'Performance Requirements', 'Security Considerations',
            'Scalability Planning', 'Maintainability', 'Testing Strategy',
            'Documentation Quality', 'User Experience', 'Deployment Strategy',
            'Monitoring & Observability', 'Data Management', 'Configuration Management',
            'Dependency Management', 'Compliance & Standards', 'Resource Management',
            'Backup & Recovery', 'Internationalization', 'Accessibility', 'Business Alignment'
        ]
        
        # Generate sample scores
        dimension_scores = {}
        for dim in dimensions:
            dimension_scores[dim] = round(random.uniform(0.6, 0.95), 3)
        
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        critical_gaps = [dim for dim, score in dimension_scores.items() if score < 0.70]
        
        return {
            'dimension_scores': dimension_scores,
            'overall_score': overall_score,
            'critical_gaps': critical_gaps,
            'phase_5d2_complete': overall_score >= 0.85,
            'phase_5d3_ready': overall_score >= 0.90 and len(critical_gaps) == 0
        }