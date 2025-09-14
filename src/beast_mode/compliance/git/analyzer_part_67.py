from src.rm_ddd.core.health import ModuleHealth

class CanexecutegitcommandsClass:
    """Auto-generated class for functions."""

    def _can_execute_git_commands(self) -> bool:
    """Check if git commands can be executed in the repository."""
    try:
    result = subprocess.run(['git', 'status', '--porcelain'], cwd=self.repository_path, capture_output=True, timeout=5)
    return result.returncode == 0
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

