from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    def create_failure_object(self, test_name: str, error_info: dict) -> TestFailureData:
        """
        Create TestFailure object from parsed information
        Requirements: 5.1 - Create comprehensive failure information
        """
        try:
            test_file, test_function, test_class = self._parse_test_name(test_name)
            failure_type = self._determine_failure_type(error_info.get('error_message', ''))
            context = self.extract_failure_context(error_info)
            return TestFailureData(test_name=test_name, test_file=test_file, failure_type=failure_type, error_message=error_info.get('error_message', 'Unknown error'), stack_trace=error_info.get('stack_trace', ''), test_function=test_function, test_class=test_class, failure_timestamp=datetime.now(), test_context=context, pytest_node_id=test_name)
        except Exception as e:
            self.logger.error(f'Failure object creation failed: {e}')
            return TestFailureData(test_name=test_name, test_file='unknown', failure_type='creation_error', error_message=f'Failed to create failure object: {e}', stack_trace='', test_function='unknown', test_class=None, failure_timestamp=datetime.now(), test_context={'creation_error': str(e)}, pytest_node_id=test_name)

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

