from src.rm_ddd.core.health import ModuleHealth

    def update_agent_collaboration_score(self, agent_id: str, score_delta: float) -> None:
        """
        Update an agent's collaboration score.
        
        Args:
            agent_id: Agent to update
            score_delta: Change in score (positive for successful collaboration)
        """
        if self.discovery_enabled:
            self.agent_registry.update_collaboration_score(agent_id, score_delta)

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

