
def _should_retry(self, error_context: ErrorContext) -> bool:
    """Determine if error should trigger retry logic"""
    return error_context.category in self.retry_config.retry_on_categories and error_context.severity.value in ['low', 'medium']
