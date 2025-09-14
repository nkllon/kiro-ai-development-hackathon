
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
    """Result of infrastructure deployment"""
    deployment_id: str
    config: GKEConfig
    status: DeploymentStatus
    deployment_time: float
    health_metrics: Dict[str, Any]
    cost_metrics: Dict[str, Any]
    security_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    created_at: datetime

@dataclass