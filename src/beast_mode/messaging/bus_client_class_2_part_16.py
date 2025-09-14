from src.rm_ddd.core.health import ModuleHealth

    def accept_help_response(self, request_id: str, response_id: str) -> bool:
        """
        Accept a help response and start collaboration.
        
        Args:
            request_id: ID of the help request
            response_id: ID of the response to accept
            
        Returns:
            bool: True if response was accepted successfully
        """
        session = self.help_system.accept_help_response(request_id, response_id)
        return session is not None

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

