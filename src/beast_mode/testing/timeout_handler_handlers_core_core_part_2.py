from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for timeout handling"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'active_timeouts': len(self.active_timeouts), 'total_operations': self.total_operations, 'timeout_warning_rate': self.timeout_warnings / max(1, self.total_operations), 'graceful_timeout_rate': self.graceful_timeouts / max(1, self.total_operations), 'hard_timeout_rate': self.hard_timeouts / max(1, self.total_operations), 'successful_degradation_rate': self.successful_degradations / max(1, self.graceful_timeouts), 'primary_timeout_seconds': self.timeout_config.primary_timeout_seconds, 'timeout_strategy': self.timeout_config.strategy.value}
