class AnalysisConfiguration(ReflectiveModule):
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
    """Configuration for analysis operations"""
    timeout_seconds: int = 300
    max_parallel_analyses: int = 4
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {'max_memory_mb': 1024, 'max_cpu_percent': 50, 'max_disk_io_mb': 100})
    analysis_thresholds: Dict[str, Any] = field(default_factory=lambda: {'max_file_size_lines': 200, 'complexity_threshold': 10.0, 'coverage_minimum': 0.8, 'performance_threshold_ms': 1000})
    safety_enabled: bool = True
    emergency_shutdown_enabled: bool = True

@dataclass(frozen=True)