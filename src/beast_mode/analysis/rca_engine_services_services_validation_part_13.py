from src.rm_ddd.core.health import ModuleHealth

def _analyze_test_structure(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test structure issues"""
    structure_analysis = {}
    if failure.context and 'test_file' in failure.context:
        test_file = failure.context['test_file']
        structure_analysis['test_file_exists'] = Path(test_file).exists()
        structure_analysis['test_file_path'] = test_file
        structure_analysis['follows_naming_convention'] = test_file.startswith('test_') or test_file.endswith('_test.py')
    return structure_analysis

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

