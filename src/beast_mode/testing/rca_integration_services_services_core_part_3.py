from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for test RCA integration capability"""
    return not self._degradation_active and self.rca_engine is not None and self.rca_engine.is_healthy() and self.performance_monitor.is_healthy() and self.timeout_handler.is_healthy()

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

