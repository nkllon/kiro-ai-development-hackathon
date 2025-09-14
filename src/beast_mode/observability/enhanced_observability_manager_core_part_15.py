
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
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str
    threshold_value: float
    severity: AlertSeverity
    evaluation_window: int = 300
    cooldown_period: int = 600
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass