from src.rm_ddd.core.health import ModuleHealth

def __init__(self, project_path: Path):
    """
        Initialize the code quality assessment engine.
        
        Args:
            project_path: Path to the project being analyzed
        """
    self.project_path = Path(project_path)
    self.logger = logging.getLogger(__name__)
    self.thresholds = {'complexity_max': 10, 'function_length_max': 50, 'class_length_max': 200, 'documentation_min': 80, 'maintainability_min': 7.0}
    self.source_patterns = ['src/**/*.py', '*.py', 'lib/**/*.py']
    self.exclude_patterns = ['test_*.py', '*_test.py', 'tests/**/*.py', '__pycache__/**', '.git/**', 'venv/**', 'env/**']
    self.logger.info(f'Code quality engine initialized for {self.project_path}')
