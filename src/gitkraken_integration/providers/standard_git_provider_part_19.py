from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class ValidaterepositoryClass:
    """Auto-generated class for functions."""

    def _validate_repository(self) -> None:
    """Validate that the repo_path is a valid git repository"""
    if not os.path.exists(self.repo_path):
    raise ValueError(f'Repository path does not exist: {self.repo_path}')
    try:
    self._run_git_command(['rev-parse', '--git-dir'])
    except subprocess.CalledProcessError:
    raise ValueError(f'Not a git repository: {self.repo_path}')

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

