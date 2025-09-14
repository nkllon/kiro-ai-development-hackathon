from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """GKE service consumer operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'active_requests': len(self.active_requests), 'queued_requests': len(self.service_queue), 'registered_teams': len(self.registered_teams), 'service_availability': {svc.value: status.value for svc, status in self.service_status.items()}, 'total_requests_served': self.service_metrics['total_requests'], 'success_rate': self._calculate_success_rate(), 'degradation_active': self._degradation_active}
