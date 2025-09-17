from src.rm_ddd.core.health import ModuleHealth

    def get_health_status(self) -> Dict[str, Any]:
        """Get client health and statistics"""
        return {'agent_id': self.agent_id, 'is_connected': self.is_connected, 'is_listening': self.is_listening, 'channel': self.channel, 'capabilities': self.capabilities, 'stats': self.stats.copy(), 'message_handlers': list(self.message_handlers.keys())}

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

