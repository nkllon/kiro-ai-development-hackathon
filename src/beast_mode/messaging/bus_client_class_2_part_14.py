from src.rm_ddd.core.health import ModuleHealth

    def cleanup_inactive_agents(self) -> int:
        """
        Manually trigger cleanup of inactive agents.
        
        Returns:
            int: Number of agents cleaned up
        """
        if not self.discovery_enabled:
            return 0
        return self.agent_registry.cleanup_inactive_agents()

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

