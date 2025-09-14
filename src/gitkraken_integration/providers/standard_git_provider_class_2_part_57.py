from src.rm_ddd.core.registry import register_module

def set_upstream_branch(self, branch_name: str, upstream: str) -> GitOperationResult:
    """Set upstream tracking branch"""
    start_time = time.time()
    try:
        self._run_git_command(['branch', '--set-upstream-to', upstream, branch_name])
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=True, message=f"Set upstream for '{branch_name}' to '{upstream}'", data={'branch_name': branch_name, 'upstream': upstream}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
        execution_time = int((time.time() - start_time) * 1000)
        suggestions = []
        if 'does not exist' in e.stderr:
            suggestions.extend([f"Upstream branch '{upstream}' does not exist", 'Check available remote branches', 'Fetch from remote first if needed'])
        return self._create_result(success=False, message=f"Failed to set upstream for '{branch_name}': {e.stderr}", error_code='GIT_SET_UPSTREAM_FAILED', suggestions=suggestions, execution_time_ms=execution_time)
