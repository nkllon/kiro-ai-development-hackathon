from src.rm_ddd.core.health import ModuleHealth

def _analyze_pytest_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze pytest failure details"""
    return {'error_type': self._get_pytest_subcategory(failure), 'has_stack_trace': failure.stack_trace is not None, 'test_context_available': bool(failure.context.get('test_file')), 'pytest_node_available': bool(failure.context.get('pytest_node_id'))}

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

