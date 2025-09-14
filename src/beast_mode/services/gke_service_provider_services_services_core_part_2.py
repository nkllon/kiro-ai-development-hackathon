from src.rm_ddd.core.health import ModuleHealth

def get_module_status(self) -> Dict[str, Any]:
    """GKE service provider operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'services_available': len([s for s in self.service_registry.values() if s['status'] == ServiceStatus.AVAILABLE]), 'active_requests': len(self.active_requests), 'gke_teams_served': len(self.gke_team_metrics), 'total_requests_served': self.service_metrics['total_requests_served'], 'success_rate': self.service_metrics['successful_requests'] / max(1, self.service_metrics['total_requests_served']), 'degradation_active': self._degradation_active}

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

