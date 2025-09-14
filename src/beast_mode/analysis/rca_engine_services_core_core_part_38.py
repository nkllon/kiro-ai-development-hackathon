from src.rm_ddd.core.health import ModuleHealth

class AnalyzemissingfilesClass:
    """Auto-generated class for functions."""

    def _analyze_missing_files(self, failure: Failure) -> Dict[str, Any]:
    """Analyze missing file issues in make context"""
    missing_files = {}
    if 'No such file' in failure.error_message:
    missing_files['has_missing_files'] = True
    if 'No such file or directory:' in failure.error_message:
    missing_files['missing_file'] = failure.error_message.split('No such file or directory:')[1].strip()
    else:
    missing_files['has_missing_files'] = False
    return missing_files

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

