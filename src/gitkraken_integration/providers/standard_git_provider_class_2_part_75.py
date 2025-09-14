from src.rm_ddd.core.registry import register_module

def get_current_branch(self) -> GitOperationResult:
    """Get current branch information"""
    start_time = time.time()
    try:
        result = self._run_git_command(['branch', '--show-current'])
        branch_name = result.stdout.strip()
        if not branch_name:
            result = self._run_git_command(['rev-parse', 'HEAD'])
            commit_hash = result.stdout.strip()
            branch_name = f'HEAD detached at {commit_hash[:7]}'
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=True, message=f'Current branch: {branch_name}', data={'branch': branch_name}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=False, message=f'Failed to get current branch: {e.stderr}', error_code='GIT_BRANCH_FAILED', execution_time_ms=execution_time)
