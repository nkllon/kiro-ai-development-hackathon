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
    """
    Monitors RM-DDD component health.
    
    Provides systematic health monitoring for RM components including
    periodic health checks, performance metrics collection, and
    health indicator aggregation.
    
    Responsibilities:
    - Periodic health check execution
    - Performance metrics collection and analysis
    - Health indicator aggregation and reporting
    - Health trend analysis and alerting
    - Integration with monitoring systems
    """
