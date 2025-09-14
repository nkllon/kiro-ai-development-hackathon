from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class GetaheadbehindcountsClass:
    """Auto-generated class for functions."""

    def _get_ahead_behind_counts(self, branch: str) -> Dict[str, int]:
    """Get ahead/behind counts for current branch"""
    try:
    result = self._run_git_command(['rev-list', '--left-right', '--count', f'{branch}...@{{u}}'])
    counts = result.stdout.strip().split('\t')
    if len(counts) == 2:
    return {'ahead': int(counts[0]), 'behind': int(counts[1])}
    except subprocess.CalledProcessError:
    pass
    return {'ahead': 0, 'behind': 0}

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

