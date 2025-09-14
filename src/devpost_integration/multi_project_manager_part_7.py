from src.rm_ddd.core.health import ModuleHealth

class GetmoduleinfoClass:
    """Auto-generated class for functions."""

    def get_module_info(self) -> Dict[str, Any]:
    """Get comprehensive module information."""
    return {
    'module_id': self.module_id,
    'version': self.version,
    'name': 'Multi Project Manager',
    'description': 'multi_project_manager module for DevPost integration',
    'author': 'DevPost Integration Team',
    'created_at': self._start_time.isoformat(),
    'interface_version': self.get_interface_version()
    }

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

