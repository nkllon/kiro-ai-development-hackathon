from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class FindgitexecutableClass:
    """Auto-generated class for functions."""

    def _find_git_executable(self) -> str:
    """Find the git executable on the system"""
    try:
    result = subprocess.run(['which', 'git'], capture_output=True, text=True, check=True)
    return result.stdout.strip()
    except subprocess.CalledProcessError:
    common_paths = ['/usr/bin/git', '/usr/local/bin/git', 'git']
    for path in common_paths:
    try:
    subprocess.run([path, '--version'], capture_output=True, check=True)
    return path
    except (subprocess.CalledProcessError, FileNotFoundError):
    continue
    raise RuntimeError('Git executable not found on system')

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

