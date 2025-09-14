from src.rm_ddd.core.health import ModuleHealth

def _attempt_recovery_with_retry(self, operation: Callable, error_context: ErrorContext, max_retries: int) -> Any:
    """Attempt recovery with retry logic"""
    try:
        return self.retry_with_simplified_parameters(operation=operation, original_error=Exception(error_context.error_message), max_retries=max_retries)
    except Exception:
        return None
