from src.rm_ddd.core.health import ModuleHealth

class GetmodulestatusClass:
    """Auto-generated class for functions."""

    def get_module_status(self) -> Dict[str, Any]:
    """GKE service consumer operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'active_requests': len(self.active_requests), 'queued_requests': len(self.service_queue), 'registered_teams': len(self.registered_teams), 'service_availability': {svc.value: status.value for svc, status in self.service_status.items()}, 'total_requests_served': self.service_metrics['total_requests'], 'success_rate': self._calculate_success_rate(), 'degradation_active': self._degradation_active}

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

