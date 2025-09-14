from src.rm_ddd.core.health import ModuleHealth

class IshealthyClass:
    """Auto-generated class for functions."""

    def is_healthy(self) -> bool:
    """Check if the git analyzer is healthy."""
    try:
    return self.repository_path.exists() and self.repository_path.is_dir() and (self.repository_path / '.git').exists() and self._can_execute_git_commands()
    except Exception:
    return False

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

