
def _is_infrastructure_failure(self, failure: Failure) -> bool:
    """Check if failure is infrastructure-related"""
    return 'PermissionError' in failure.error_message or 'ConnectionError' in failure.error_message or 'system' in failure.component.lower() or ('environment' in failure.error_message.lower())
