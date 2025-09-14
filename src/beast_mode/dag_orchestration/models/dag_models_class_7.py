class RiskFactor(ReflectiveModule):
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
    """Individual risk factor in execution plan."""
    risk_id: str
    risk_type: RiskType
    probability: float  # 0.0 to 1.0
    impact: RiskImpact
    affected_tasks: List[str]
    mitigation_strategy: Optional[str] = None
    
    def __post_init__(self) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate risk factor data."""
        if not (0.0 <= self.probability <= 1.0):
            raise ValueError("Probability must be between 0.0 and 1.0")


@dataclass