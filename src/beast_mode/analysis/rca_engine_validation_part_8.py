
def _is_pytest_failure(self, failure: Failure) -> bool:
    """Check if failure is pytest-related"""
    return 'pytest' in failure.error_message.lower() or 'test_' in failure.component or failure.context.get('pytest_node_id') is not None or ('ImportError' in failure.error_message) or ('AssertionError' in failure.error_message)
