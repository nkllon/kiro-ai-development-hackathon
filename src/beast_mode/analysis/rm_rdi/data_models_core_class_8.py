from src.rm_ddd.core.registry import register_module
class ArchitectureAnalysis(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
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
    """Architecture analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    rm_architecture_score: float
    rdi_architecture_score: float
    integration_quality_score: float
    scalability_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_areas: List[str]
    safety_validated: bool = True

@dataclass(frozen=True)
    def __init__(self):
        register_module('ArchitectureAnalysis', self)