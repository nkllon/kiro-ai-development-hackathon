from src.rm_ddd.core.health import ModuleHealth

    def find_agents_with_all_capabilities(self, required_capabilities: List[str]) -> List[DiscoveredAgent]:
        """
        Find agents that have ALL of the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            List[DiscoveredAgent]: Agents with all matching capabilities
        """
        if not self.discovery_enabled:
            return []
        return self.agent_registry.find_agents_with_all_capabilities(required_capabilities)

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

