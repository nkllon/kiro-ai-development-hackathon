
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
