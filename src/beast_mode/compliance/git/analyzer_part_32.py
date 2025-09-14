from src.rm_ddd.core.health import ModuleHealth

def _get_commit_hashes_ahead(self, target_branch: str, base_branch: str) -> List[str]:
    """Get commit hashes that are ahead of the base branch."""
    try:
        cmd = ['git', 'rev-list', f'{base_branch}..{target_branch}', '--reverse']
        result = subprocess.run(cmd, cwd=self.repository_path, capture_output=True, text=True, timeout=self._config['git_timeout'])
        if result.returncode != 0:
            self.logger.error(f'Git command failed: {result.stderr}')
            return []
        commit_hashes = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return commit_hashes
    except subprocess.TimeoutExpired:
        self.logger.error('Git command timed out')
        return []
    except Exception as e:
        self.logger.error(f'Error getting commit hashes: {str(e)}')
        return []
