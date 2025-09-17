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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

