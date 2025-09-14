from src.rm_ddd.core.health import ModuleHealth

def _generate_failure_signature(self, failure: Failure) -> str:
    """Generate unique signature for failure pattern matching"""
    signature_parts = [failure.component, failure.category.value, failure.error_message[:100] if failure.error_message else '', str(sorted(failure.context.keys())) if failure.context else '']
    return '|'.join(signature_parts)

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

