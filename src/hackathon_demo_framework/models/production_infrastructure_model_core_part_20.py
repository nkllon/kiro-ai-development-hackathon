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
    """Configuration for GKE cluster deployment"""
    cluster_name: str
    node_count: int
    machine_type: str
    region: str
    auto_scaling: bool
    security_policies: List[str]
    monitoring_enabled: bool
    cost_optimization: CostOptimizationLevel

@dataclass