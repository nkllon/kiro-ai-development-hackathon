from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class MergebranchClass:
    """Auto-generated class for functions."""

    def merge_branch(self, source: str, target: str=None) -> GitOperationResult:
    """Merge branches"""
    start_time = time.time()
    try:
    if target:
    switch_result = self.switch_branch(target)
    if not switch_result.success:
    return switch_result
    self._run_git_command(['merge', source])
    execution_time = int((time.time() - start_time) * 1000)
    return self._create_result(success=True, message=f"Successfully merged '{source}' into current branch", data={'source_branch': source, 'target_branch': target, 'conflicts': False}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
    execution_time = int((time.time() - start_time) * 1000)
    if 'CONFLICT' in e.stdout or 'Automatic merge failed' in e.stdout:
    conflicts = self.get_merge_conflicts()
    return GitOperationResult(success=False, status=GitOperationStatus.CONFLICT, message=f"Merge conflicts detected when merging '{source}'", data={'source_branch': source, 'target_branch': target, 'conflicts': True, 'conflict_files': conflicts.data.get('conflicts', []) if conflicts.success else []}, provider_used='Standard Git', execution_time_ms=execution_time, error_code='GIT_MERGE_CONFLICT', suggestions=['Resolve conflicts manually', 'Use get_merge_conflicts() to see conflicted files', "Run 'git add' after resolving conflicts", "Complete merge with 'git commit'"])
    return self._create_result(success=False, message=f"Failed to merge '{source}': {e.stderr}", error_code='GIT_MERGE_FAILED', execution_time_ms=execution_time)

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

