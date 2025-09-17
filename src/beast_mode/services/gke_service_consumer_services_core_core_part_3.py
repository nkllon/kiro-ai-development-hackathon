from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for GKE service consumer"""
    core_services_healthy = all((status != ServiceStatus.UNAVAILABLE for status in self.service_status.values()))
    components_healthy = self.pdca_orchestrator.is_healthy() and self.registry_intelligence.is_healthy() and self.makefile_health_manager.is_healthy() and self.test_suite.is_healthy()
    return core_services_healthy and components_healthy and (not self._degradation_active)

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

