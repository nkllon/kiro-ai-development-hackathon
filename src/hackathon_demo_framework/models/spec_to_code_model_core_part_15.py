
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
    """RDI Compliance: Links model functionality to specific requirements"""
    requirement_id: str
    requirement_text: str
    implementation_method: str
    validation_criteria: str
    traceability_score: float

@dataclass