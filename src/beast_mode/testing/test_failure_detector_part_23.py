from src.rm_ddd.core.health import ModuleHealth

    def _create_parsing_failure(self, test_command: str, error: str) -> TestFailureData:
        """Create failure object for parsing errors"""
        return TestFailureData(test_name='test_parsing_error', test_file='parsing', failure_type='parsing_error', error_message=f'Test output parsing failed: {error}', stack_trace=f'Command: {test_command}\nParsing Error: {error}', test_function='parsing', test_class=None, failure_timestamp=datetime.now(), test_context={'parsing_error': True, 'command': test_command}, pytest_node_id='parsing::error')

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

