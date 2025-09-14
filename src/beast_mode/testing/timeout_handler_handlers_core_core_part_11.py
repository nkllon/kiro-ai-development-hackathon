from src.rm_ddd.core.health import ModuleHealth

def _create_timeout_context(self, operation_id: str) -> Dict[str, Any]:
    """Create timeout context for operation"""
    return {'operation_id': operation_id, 'timeout_config': self.timeout_config, 'start_time': datetime.now(), 'check_timeout': lambda: self._check_operation_timeout(operation_id), 'request_degradation': lambda level=1: self.apply_graceful_degradation(operation_id, level)}

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

