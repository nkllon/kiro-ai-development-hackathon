from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        recent_indicators = [indicator for indicator in self._health_indicators if (datetime.now() - indicator.timestamp).total_seconds() < 300]
        critical_count = sum((1 for indicator in recent_indicators if indicator.status == 'critical'))
        return critical_count == 0

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

