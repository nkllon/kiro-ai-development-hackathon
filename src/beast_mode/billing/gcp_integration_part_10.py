from src.rm_ddd.core.health import ModuleHealth

    def _is_cache_valid(self) -> bool:
        """Check if cached metrics are still valid"""
        if not self.cached_metrics or not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_duration

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

