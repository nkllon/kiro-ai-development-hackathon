from src.rm_ddd.core.health import ModuleHealth

def _create_monitoring_failure(self, test_command: str, error: str) -> TestFailureData:
    """Create failure object for monitoring errors"""
    return TestFailureData(test_name='test_monitoring_error', test_file='monitoring', failure_type='monitoring_error', error_message=f'Test monitoring failed: {error}', stack_trace=f'Command: {test_command}\nError: {error}', test_function='monitoring', test_class=None, failure_timestamp=datetime.now(), test_context={'monitoring_error': True, 'command': test_command}, pytest_node_id='monitoring::error')
