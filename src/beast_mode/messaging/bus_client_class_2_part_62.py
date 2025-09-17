from src.rm_ddd.core.health import ModuleHealth

def is_agent_available_for_collaboration(self, agent_id: str, at_time: Optional[datetime]=None) -> bool:
    """Check if an agent is available for collaboration"""
    return self.collaboration_scheduler.is_agent_available(agent_id, at_time)

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

