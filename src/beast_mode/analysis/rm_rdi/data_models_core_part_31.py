from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Individual recommendation with safety metadata"""
    recommendation_id: str
    title: str
    description: str
    priority: Priority
    category: RecommendationCategory
    effort_estimate: EffortEstimate
    impact_assessment: ImpactAssessment
    implementation_guidance: str
    success_criteria: List[str]
    safety_notes: List[str] = field(default_factory=list)
    rollback_plan: str = ''

@dataclass(frozen=True)