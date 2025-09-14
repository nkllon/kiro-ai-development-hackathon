from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def unset_upstream_branch(self, branch_name: str) -> GitOperationResult:
    """Unset upstream tracking branch"""
    start_time = time.time()
    try:
        self._run_git_command(['branch', '--unset-upstream', branch_name])
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=True, message=f"Unset upstream for branch '{branch_name}'", data={'branch_name': branch_name}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
        execution_time = int((time.time() - start_time) * 1000)
        suggestions = []
        if 'no upstream' in e.stderr.lower():
            suggestions.append(f"Branch '{branch_name}' has no upstream branch set")
        return self._create_result(success=False, message=f"Failed to unset upstream for '{branch_name}': {e.stderr}", error_code='GIT_UNSET_UPSTREAM_FAILED', suggestions=suggestions, execution_time_ms=execution_time)
