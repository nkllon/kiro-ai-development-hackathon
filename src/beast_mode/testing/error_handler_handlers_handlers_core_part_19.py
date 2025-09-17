from src.rm_ddd.core.health import ModuleHealth

def _attempt_recovery_with_retry(self, operation: Callable, error_context: ErrorContext, max_retries: int) -> Any:
    """Attempt recovery with retry logic"""
    try:
        return self.retry_with_simplified_parameters(operation=operation, original_error=Exception(error_context.error_message), max_retries=max_retries)
    except Exception:
        return None

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

