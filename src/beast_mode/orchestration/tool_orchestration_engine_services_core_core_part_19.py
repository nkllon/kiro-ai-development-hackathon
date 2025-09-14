from src.rm_ddd.core.health import ModuleHealth

def _generate_failure_signature(self, failure_context: Dict[str, Any]) -> str:
    """Generate signature for failure pattern matching"""
    signature_parts = [failure_context.get('tool_name', 'unknown'), failure_context.get('error_type', 'unknown'), failure_context.get('failure_category', 'unknown'), str(failure_context.get('exit_code', 'unknown'))]
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

