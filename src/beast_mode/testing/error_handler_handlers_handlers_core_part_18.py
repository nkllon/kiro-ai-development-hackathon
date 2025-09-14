from src.rm_ddd.core.health import ModuleHealth

def _should_retry(self, error_context: ErrorContext) -> bool:
    """Determine if error should trigger retry logic"""
    return error_context.category in self.retry_config.retry_on_categories and error_context.severity.value in ['low', 'medium']

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

