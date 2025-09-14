from src.rm_ddd.core.health import ModuleHealth

    def get_discovered_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
        """Get a specific discovered agent by ID"""
        if not self.discovery_enabled:
            return None
        return self.agent_registry.get_agent(agent_id)

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

