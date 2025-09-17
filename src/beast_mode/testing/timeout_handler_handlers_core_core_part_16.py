from src.rm_ddd.core.health import ModuleHealth

def _handle_hard_timeout(self, operation_id: str) -> None:
    """Handle hard timeout"""
    try:
        self.hard_timeouts += 1
        self.logger.error(f'Operation {operation_id} exceeded hard timeout ({self.timeout_config.hard_timeout_seconds}s)')
        self._apply_hard_timeout(operation_id)
    except Exception as e:
        self.logger.error(f'Hard timeout handling failed for operation {operation_id}: {e}')

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

