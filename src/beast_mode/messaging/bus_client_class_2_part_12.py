
    def get_all_capabilities(self) -> Set[str]:
        """Get all unique capabilities across all discovered agents"""
        if not self.discovery_enabled:
            return set()
        return self.agent_registry.get_all_capabilities()
