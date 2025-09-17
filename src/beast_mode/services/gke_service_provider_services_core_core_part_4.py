from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for GKE service provider"""
    return {'service_availability': {'status': 'healthy' if self.is_healthy() else 'degraded', 'available_services': len([s for s in self.service_registry.values() if s['status'] == ServiceStatus.AVAILABLE]), 'total_services': len(self.service_registry), 'service_details': {service_type.value: {'status': service_info['status'].value, 'current_load': service_info['current_load'], 'max_concurrent': service_info['max_concurrent'], 'utilization': service_info['current_load'] / service_info['max_concurrent']} for service_type, service_info in self.service_registry.items()}}, 'dependency_health': {'status': 'healthy' if all([self.pdca_orchestrator.is_healthy(), self.registry_engine.is_healthy(), self.makefile_manager.is_healthy()]) else 'degraded', 'pdca_orchestrator': self.pdca_orchestrator.is_healthy(), 'registry_engine': self.registry_engine.is_healthy(), 'makefile_manager': self.makefile_manager.is_healthy()}, 'performance_metrics': {'status': 'healthy' if self.service_metrics['successful_requests'] / max(1, self.service_metrics['total_requests_served']) >= 0.95 else 'degraded', 'success_rate': self.service_metrics['successful_requests'] / max(1, self.service_metrics['total_requests_served']), 'average_response_time': self.service_metrics['average_response_time'], 'gke_teams_served': len(self.gke_team_metrics)}}

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

