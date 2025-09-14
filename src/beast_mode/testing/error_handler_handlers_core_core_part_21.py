
def _generate_emergency_fallback(self, failure: Failure, error_message: str) -> FallbackReportData:
    """Generate emergency fallback when all else fails"""
    return FallbackReportData(error_summary=f'Emergency fallback: {error_message}', basic_failure_info=[{'failure_id': failure.failure_id, 'error': 'Multiple system failures'}], suggested_actions=['Contact system administrator', 'Check system health', 'Review logs immediately'], health_status={'emergency': True}, timestamp=datetime.now(), degradation_level=DegradationLevel.EMERGENCY)
