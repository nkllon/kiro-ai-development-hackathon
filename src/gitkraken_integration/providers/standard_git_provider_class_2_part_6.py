from src.rm_ddd.core.registry import register_module

    def _validate_repository(self) -> None:
        """Validate that the repo_path is a valid git repository"""
        if not os.path.exists(self.repo_path):
            raise ValueError(f'Repository path does not exist: {self.repo_path}')
        try:
            self._run_git_command(['rev-parse', '--git-dir'])
        except subprocess.CalledProcessError:
            raise ValueError(f'Not a git repository: {self.repo_path}')
