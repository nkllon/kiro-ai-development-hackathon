from src.rm_ddd.core.health import ModuleHealth

class CheckinstallationintegrityClass:
    """Auto-generated class for functions."""

    def _check_installation_integrity(self, tool_name: str) -> Dict[str, Any]:
    """Check if tool files are missing or corrupted"""
    if tool_name == 'makefile':
    makefiles_dir = Path('makefiles')
    if not makefiles_dir.exists():
    return {'healthy': False, 'issues': ['makefiles/ directory missing'], 'root_causes': ['modular_makefile_structure_not_created']}
    return {'healthy': True, 'issues': [], 'root_causes': []}

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

