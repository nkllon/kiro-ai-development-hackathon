
def is_healthy(self) -> bool:
    """Check if the git analyzer is healthy."""
    try:
        return self.repository_path.exists() and self.repository_path.is_dir() and (self.repository_path / '.git').exists() and self._can_execute_git_commands()
    except Exception:
        return False
