from src.rm_ddd.core.health import ModuleHealth

def _get_avg_operation_time(self) -> float:
    """Get average operation time in milliseconds"""
    if not self._operation_times:
        return 0.0
    return sum(self._operation_times) / len(self._operation_times)

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

