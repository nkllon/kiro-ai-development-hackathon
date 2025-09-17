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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

