from src.rm_ddd.core.health import ModuleHealth

    def clear_errors(self) -> None:
        """Clear all validation errors."""
        try:
            self.errors.clear()
            self.is_valid = True
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to clear errors: {e}")
            self._errors += 1

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

    