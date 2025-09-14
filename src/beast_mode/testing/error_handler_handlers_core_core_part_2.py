from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for external systems"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'total_errors_handled': self.total_errors_handled, 'successful_recoveries': self.successful_recoveries, 'fallback_reports_generated': self.fallback_reports_generated, 'retry_success_rate': self.successful_retries / max(1, self.retry_attempts_made), 'current_degradation_level': self.degradation_level.value, 'component_health_summary': self._get_component_health_summary(), 'degradation_active': self._degradation_active}
