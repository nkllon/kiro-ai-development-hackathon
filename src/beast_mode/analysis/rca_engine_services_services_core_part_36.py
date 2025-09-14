from src.rm_ddd.core.health import ModuleHealth

def _analyze_syntax_issues(self, failure: Failure) -> Dict[str, Any]:
    """Analyze syntax-related issues"""
    syntax_analysis = {}
    if 'SyntaxError' in failure.error_message or (failure.stack_trace and 'SyntaxError' in failure.stack_trace):
        syntax_analysis['has_syntax_error'] = True
        syntax_analysis['syntax_error_details'] = failure.error_message
    else:
        syntax_analysis['has_syntax_error'] = False
    return syntax_analysis

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

