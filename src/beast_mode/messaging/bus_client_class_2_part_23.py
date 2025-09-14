from src.rm_ddd.core.health import ModuleHealth

    def set_message_callback(self, callback_name: str, callback: Callable) -> None:
        """
        Set a callback for the message router.
        
        Args:
            callback_name: Name of the callback (e.g., 'on_simple_message')
            callback: Callback function
        """
        if self.message_router:
            self.message_router.set_callback(callback_name, callback)
        else:
            logger.warning('Message router not initialized, callback not set')

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

