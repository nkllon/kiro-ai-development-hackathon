from src.rm_ddd.core.health import ModuleHealth

    def get_discovery_stats(self) -> Dict:
        """Get agent discovery statistics"""
        if not self.discovery_enabled:
            return {'discovery_enabled': False}
        return {'discovery_enabled': True, **self.agent_registry.get_registry_stats()}

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

