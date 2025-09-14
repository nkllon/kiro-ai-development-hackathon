from src.rm_ddd.core.health import ModuleHealth

    def _create_parsing_failure(self, test_command: str, error: str) -> TestFailureData:
        """Create failure object for parsing errors"""
        return TestFailureData(test_name='test_parsing_error', test_file='parsing', failure_type='parsing_error', error_message=f'Test output parsing failed: {error}', stack_trace=f'Command: {test_command}\nParsing Error: {error}', test_function='parsing', test_class=None, failure_timestamp=datetime.now(), test_context={'parsing_error': True, 'command': test_command}, pytest_node_id='parsing::error')
