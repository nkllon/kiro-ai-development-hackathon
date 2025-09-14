from src.rm_ddd.core.health import ModuleHealth

class AnalyzetestfailurecategorizationClass:
    """Auto-generated class for functions."""

    def analyze_test_failure_categorization(self, failure: Failure) -> Dict[str, Any]:
    """
    Categorize test failures (pytest, make, infrastructure) - Requirement 5.1, 5.2, 5.3
    """
    try:
    self.logger.info(f'Categorizing test failure: {failure.failure_id}')
    categorization = {'primary_category': 'unknown', 'subcategory': 'unknown', 'confidence': 0.0, 'analysis_details': {}}
    if self._is_pytest_failure(failure):
    categorization.update({'primary_category': 'pytest_failure', 'subcategory': self._get_pytest_subcategory(failure), 'confidence': 0.9, 'analysis_details': self._analyze_pytest_details(failure)})
    elif self._is_make_failure(failure):
    categorization.update({'primary_category': 'make_target_failure', 'subcategory': self._get_make_subcategory(failure), 'confidence': 0.8, 'analysis_details': self._analyze_make_details(failure)})
    elif self._is_infrastructure_failure(failure):
    categorization.update({'primary_category': 'infrastructure_failure', 'subcategory': self._get_infrastructure_subcategory(failure), 'confidence': 0.7, 'analysis_details': self._analyze_infrastructure_details(failure)})
    elif failure.component.startswith('test:') or 'test' in failure.component.lower() or (failure.context and 'test_file' in failure.context):
    categorization.update({'primary_category': 'test_environment_failure', 'subcategory': 'unknown_test_failure', 'confidence': 0.5, 'analysis_details': {'error': 'Could not categorize test failure specifically'}})
    self.logger.info(f"Test failure categorized as: {categorization['primary_category']}/{categorization['subcategory']}")
    return categorization
    except Exception as e:
    self.logger.error(f'Test failure categorization failed: {e}')
    return {'primary_category': 'unknown', 'subcategory': 'categorization_error', 'confidence': 0.0, 'analysis_details': {'error': str(e)}}

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

