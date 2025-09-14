from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, project_path: Path):
        """
        Initialize the functionality validator.
        
        Args:
            project_path: Path to the project being validated
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.test_patterns = ['test_*.py', '*_test.py', 'tests/*.py', 'test/**/*.py']
        self.source_patterns = ['src/**/*.py', '*.py', 'lib/**/*.py']
        self.required_files = ['README.md', 'requirements.txt', 'pyproject.toml']
        self.logger.info(f'Functionality validator initialized for {self.project_path}')

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

