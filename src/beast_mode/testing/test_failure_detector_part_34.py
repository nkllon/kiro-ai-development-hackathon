from src.rm_ddd.core.health import ModuleHealth

def _create_timeout_failure(self, test_command: str) -> TestFailureData:
    """Create failure object for test execution timeout"""
    return TestFailureData(test_name='test_execution_timeout', test_file='timeout', failure_type='timeout', error_message=f'Test execution timeout: {test_command}', stack_trace='Test execution exceeded 5 minute timeout', test_function='timeout', test_class=None, failure_timestamp=datetime.now(), test_context={'timeout': True, 'command': test_command}, pytest_node_id='timeout::execution')

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

