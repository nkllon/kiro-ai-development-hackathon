from src.rm_ddd.core.health import ModuleHealth

def __init__(self, repository_path: str='.'):
    """
        Initialize the GitAnalyzer.
        
        Args:
            repository_path: Path to the git repository to analyze
        """
    super().__init__('GitAnalyzer')
    self.repository_path = Path(repository_path).resolve()
    self.logger = logging.getLogger(__name__)
    self._config = {'target_branch': 'main', 'base_branch': 'origin/master', 'max_commits_to_analyze': 10, 'git_timeout': 30}
    self.logger.info(f'GitAnalyzer initialized for repository: {self.repository_path}')
