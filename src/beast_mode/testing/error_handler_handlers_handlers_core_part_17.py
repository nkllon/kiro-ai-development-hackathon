
def _assess_error_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
    """Assess error severity based on type and category"""
    critical_categories = [ErrorCategory.RCA_ENGINE_FAILURE, ErrorCategory.RESOURCE_EXHAUSTION]
    high_categories = [ErrorCategory.TIMEOUT_EXCEEDED, ErrorCategory.CONFIGURATION_ERROR]
    if category in critical_categories:
        return ErrorSeverity.CRITICAL
    elif category in high_categories:
        return ErrorSeverity.HIGH
    elif 'critical' in str(error).lower():
        return ErrorSeverity.CRITICAL
    elif 'error' in str(error).lower():
        return ErrorSeverity.MEDIUM
    else:
        return ErrorSeverity.LOW
