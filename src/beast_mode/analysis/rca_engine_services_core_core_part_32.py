from src.rm_ddd.core.health import ModuleHealth

class AnalyzemakedetailsClass:
    """Auto-generated class for functions."""

    def _analyze_make_details(self, failure: Failure) -> Dict[str, Any]:
    """Analyze make failure details"""
    return {'error_type': self._get_make_subcategory(failure), 'makefile_exists': Path('Makefile').exists(), 'makefiles_dir_exists': Path('makefiles').exists(), 'error_in_makefile': 'Makefile' in failure.error_message}

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

