from datetime import datetime
from typing import Dict, List, Any

def create_branch(self, name: str, from_branch: str='HEAD') -> GitOperationResult:
    """Create a new branch"""
    start_time = time.time()
    if not self.validate_branch_name(name):
        return self._create_result(success=False, message=f'Invalid branch name: {name}', error_code='GIT_INVALID_BRANCH_NAME', suggestions=['Branch names cannot contain spaces or special characters', 'Use hyphens or underscores instead of spaces', 'Avoid starting with dots or ending with slashes'])
    try:
        self._run_git_command(['checkout', '-b', name, from_branch])
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=True, message=f"Created and switched to branch '{name}' from '{from_branch}'", data={'branch_name': name, 'from_branch': from_branch, 'switched': True}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
        execution_time = int((time.time() - start_time) * 1000)
        suggestions = ['Check if branch name already exists']
        if 'already exists' in e.stderr:
            suggestions.append(f"Use 'git checkout {name}' to switch to existing branch")
        return self._create_result(success=False, message=f"Failed to create branch '{name}': {e.stderr}", error_code='GIT_CREATE_BRANCH_FAILED', suggestions=suggestions, execution_time_ms=execution_time)
