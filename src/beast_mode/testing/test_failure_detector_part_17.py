from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

class CreatefailuredataClass:
    """Auto-generated class for functions."""

    def _create_failure_data(self, test_name: str, traceback: List[str], error_lines: List[str]) -> Optional[TestFailureData]:
    """Create failure data from parsed text output"""
    try:
    if not error_lines and (not traceback):
    return None
    test_file, test_function, test_class = self._parse_test_name(test_name)
    error_message = ' '.join(error_lines) if error_lines else 'Unknown error'
    stack_trace = '\n'.join(traceback) if traceback else ''
    failure_type = self._determine_failure_type(error_message)
    return TestFailureData(test_name=test_name, test_file=test_file, failure_type=failure_type, error_message=error_message, stack_trace=stack_trace, test_function=test_function, test_class=test_class, failure_timestamp=datetime.now(), test_context={'text_source': True}, pytest_node_id=test_name)
    except Exception as e:
    self.logger.error(f'Failed to create failure data: {e}')
    return None

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

    def register_module(self, registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
    registry.register(self.get_interface_metadata())

    def health_check(self):
    """Perform health check."""
    return {
    'status': 'healthy',
    'timestamp': datetime.now().isoformat(),
    'module_id': getattr(self, 'module_id', self.__class__.__name__)
    }

    def get_health_status(self):
    """Get current health status."""
    return self.health_check()

