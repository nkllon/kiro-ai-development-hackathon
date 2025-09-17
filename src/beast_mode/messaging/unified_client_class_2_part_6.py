from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def get_status(self) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """
        Get comprehensive client status.
        
        Returns:
            Dictionary containing status information
        """
        transport_status = self.transport.get_status()
        return {'agent_id': self.agent_id, 'transport_type': self.transport_type, 'is_started': self.is_started, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_status': transport_status, 'stats': self.stats.copy(), 'message_handlers': {str(msg_type): len(handlers) for msg_type, handlers in self.message_handlers.items()}}

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

