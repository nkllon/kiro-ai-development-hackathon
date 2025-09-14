from datetime import datetime
from typing import Dict, List, Any

    def get_health_status(self) -> GitOperationResult:
        """Get provider health status for monitoring"""
        start_time = time.time()
        try:
            version_result = self._run_git_command(['--version'])
            git_version = version_result.stdout.strip()
            status_result = self._run_git_command(['status', '--porcelain'])
            remote_accessible = True
            try:
                self._run_git_command(['ls-remote', '--heads', 'origin'], timeout=5)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                remote_accessible = False
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=True, message='Standard Git provider is healthy', data={'git_version': git_version, 'repository_accessible': True, 'remote_accessible': remote_accessible, 'git_executable': self.git_executable, 'repo_path': self.repo_path}, execution_time_ms=execution_time)
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=False, message=f'Standard Git provider health check failed: {e.stderr}', error_code='GIT_HEALTH_CHECK_FAILED', execution_time_ms=execution_time)
