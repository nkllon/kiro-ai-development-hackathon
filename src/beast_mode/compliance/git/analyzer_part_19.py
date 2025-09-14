
    def _can_execute_git_commands(self) -> bool:
        """Check if git commands can be executed in the repository."""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], cwd=self.repository_path, capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
