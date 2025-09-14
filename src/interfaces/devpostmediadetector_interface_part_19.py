from src.rm_ddd.core.health import ModuleHealth

    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._files_processed = 0
        self._files_detected = 0
        self._errors = 0
        self._start_time = datetime.now()

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

        logger.info("Metrics reset for media detector module")