
def _generate_fallback_report(self, failure: Failure, error_context: ErrorContext) -> FallbackReportData:
    """Generate fallback report for single failure"""
    return FallbackReportData(error_summary=f'RCA analysis failed: {error_context.error_message[:200]}', basic_failure_info=[{'failure_id': failure.failure_id, 'component': failure.component, 'error_message': failure.error_message[:200], 'timestamp': failure.timestamp.isoformat()}], suggested_actions=['Check RCA engine configuration', 'Verify system resources', 'Review error logs for details', 'Retry with simplified parameters'], health_status=self.get_health_indicators(), timestamp=datetime.now(), degradation_level=self.degradation_level)
