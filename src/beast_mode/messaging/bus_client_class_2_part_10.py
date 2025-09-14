from src.rm_ddd.core.health import ModuleHealth

    def get_discovered_agents(self) -> List[DiscoveredAgent]:
        """Get all discovered agents"""
        if not self.discovery_enabled:
            return []
        return self.agent_registry.get_active_agents()
