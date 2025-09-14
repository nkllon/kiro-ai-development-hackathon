from src.rm_ddd.core.health import ModuleHealth

    def clear_domain_events(self):
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Clear domain events after publishing."""
        event_count = len(self._domain_events)
        self._domain_events.clear()
        if event_count > 0:
            logger.debug(f'Cleared {event_count} domain events from {self.__class__.__name__}({self.id})')

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

