
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
    Global registry for RM-DDD components.
    
    Provides centralized component discovery, health monitoring, and
    dependency management for all RM components in the system.
    
    Responsibilities:
    - Component registration and discovery
    - Health status aggregation and monitoring
    - Dependency tracking and resolution
    - Service discovery and load balancing
    - System-wide health reporting
    
    Accountability Chain:
    - Registry Manager: Responsible for registry operations
    - Component Owners: Responsible for component health
    - System Administrator: Responsible for overall system health
    """
