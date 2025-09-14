from src.rm_ddd.core.registry import register_module

def list_branches(self, include_remote: bool=True) -> GitOperationResult:
    """List all branches with comprehensive metadata"""
    start_time = time.time()
    try:
        args = ['branch', '-vv']
        if include_remote:
            args.append('--all')
        result = self._run_git_command(args)
        branches = self._parse_branch_output(result.stdout)
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=True, message=f'Found {len(branches)} branches', data={'branches': [branch.__dict__ for branch in branches], 'total_count': len(branches), 'local_count': len([b for b in branches if not b.name.startswith('remotes/')]), 'remote_count': len([b for b in branches if b.name.startswith('remotes/')])}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
        execution_time = int((time.time() - start_time) * 1000)
        return self._create_result(success=False, message=f'Failed to list branches: {e.stderr}', error_code='GIT_BRANCH_LIST_FAILED', execution_time_ms=execution_time)
