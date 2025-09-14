from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class RenamebranchClass:
    """Auto-generated class for functions."""

    def rename_branch(self, old_name: str, new_name: str) -> GitOperationResult:
    """Rename a branch"""
    start_time = time.time()
    if not self.validate_branch_name(new_name):
    return self._create_result(success=False, message=f'Invalid new branch name: {new_name}', error_code='GIT_INVALID_BRANCH_NAME', suggestions=['Branch names cannot contain spaces or special characters', 'Use hyphens or underscores instead of spaces'])
    try:
    try:
    self._run_git_command(['show-ref', '--verify', f'refs/heads/{old_name}'])
    except subprocess.CalledProcessError:
    return self._create_result(success=False, message=f"Branch '{old_name}' does not exist", error_code='GIT_BRANCH_NOT_FOUND', suggestions=[f'Check available branches with list_branches()'])
    self._run_git_command(['branch', '-m', old_name, new_name])
    execution_time = int((time.time() - start_time) * 1000)
    return self._create_result(success=True, message=f"Renamed branch '{old_name}' to '{new_name}'", data={'old_name': old_name, 'new_name': new_name}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
    execution_time = int((time.time() - start_time) * 1000)
    suggestions = []
    if 'already exists' in e.stderr:
    suggestions.append(f"Branch '{new_name}' already exists")
    suggestions.append('Choose a different name or delete the existing branch first')
    return self._create_result(success=False, message=f"Failed to rename branch '{old_name}' to '{new_name}': {e.stderr}", error_code='GIT_RENAME_BRANCH_FAILED', suggestions=suggestions, execution_time_ms=execution_time)

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

