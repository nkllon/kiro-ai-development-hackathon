
    def _create_failure_from_json(self, test_data: dict) -> Optional[TestFailureData]:
        """Create failure data from JSON test information"""
        try:
            node_id = test_data.get('nodeid', 'unknown')
            test_file, test_function, test_class = self._parse_test_name(node_id)
            call_info = test_data.get('call', {})
            error_message = call_info.get('longrepr', 'Unknown error')
            stack_trace = ''
            if 'traceback' in call_info:
                stack_trace = '\n'.join([entry.get('line', '') for entry in call_info['traceback']])
            failure_type = self._determine_failure_type(error_message)
            return TestFailureData(test_name=node_id, test_file=test_file, failure_type=failure_type, error_message=error_message, stack_trace=stack_trace, test_function=test_function, test_class=test_class, failure_timestamp=datetime.now(), test_context={'json_source': True, 'duration': test_data.get('duration', 0)}, pytest_node_id=node_id)
        except Exception as e:
            self.logger.error(f'Failed to create failure from JSON: {e}')
            return None
