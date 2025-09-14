from src.rm_ddd.core.registry import register_module

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
