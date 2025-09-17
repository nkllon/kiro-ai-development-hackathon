from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for timeout handling capability"""
    if self.total_operations == 0:
        return not self._degradation_active
    hard_timeout_rate = self.hard_timeouts / max(1, self.total_operations)
    degradation_success_rate = self.successful_degradations / max(1, self.graceful_timeouts) if self.graceful_timeouts > 0 else 1.0
    return not self._degradation_active and hard_timeout_rate < 0.05 and (degradation_success_rate > 0.8)

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

