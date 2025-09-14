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
