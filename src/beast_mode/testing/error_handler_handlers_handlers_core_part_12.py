
def get_error_report(self) -> Dict[str, Any]:
    """Get comprehensive error handling report"""
    try:
        recent_errors = [{'error_id': error.error_id, 'timestamp': error.timestamp.isoformat(), 'severity': error.severity.value, 'category': error.category.value, 'component': error.component, 'operation': error.operation, 'message': error.error_message[:200]} for error in self.error_history[-10:]]
        return {'error_handling_summary': {'total_errors_handled': self.total_errors_handled, 'successful_recoveries': self.successful_recoveries, 'recovery_rate': self.successful_recoveries / max(1, self.total_errors_handled), 'fallback_reports_generated': self.fallback_reports_generated, 'current_degradation_level': self.degradation_level.value}, 'retry_statistics': {'retry_attempts_made': self.retry_attempts_made, 'successful_retries': self.successful_retries, 'retry_success_rate': self.successful_retries / max(1, self.retry_attempts_made)}, 'component_health': {name: {'is_healthy': metrics.is_healthy, 'error_count_last_hour': metrics.error_count_last_hour, 'success_rate_last_hour': metrics.success_rate_last_hour, 'average_response_time_ms': metrics.average_response_time_ms, 'degradation_level': metrics.degradation_level.value} for name, metrics in self.component_health.items()}, 'recent_errors': recent_errors, 'health_indicators': self.get_health_indicators()}
    except Exception as e:
        self.logger.error(f'Error report generation failed: {e}')
        return {'error': f'Error report generation failed: {e}', 'timestamp': datetime.now().isoformat()}
