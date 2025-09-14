from src.rm_ddd.core.registry import register_module

    def __init__(self, project_path: Path):
        """Initialize content analyzer."""
        self.project_path = Path(project_path).resolve()
        self._content_cache: Dict[str, str] = {}
        self._git_repo: Optional['git.Repo'] = None
        if GIT_AVAILABLE:
            try:
                self._git_repo = git.Repo(self.project_path, search_parent_directories=True)
            except (git.InvalidGitRepositoryError, git.GitCommandError):
                logger.debug('No Git repository found or Git not available')
                self._git_repo = None
