from src.rm_ddd.core.health import ModuleHealth

def _analyze_service_usage_patterns(self) -> Dict[str, Any]:
    """Analyze service usage patterns across GKE teams"""
    usage_patterns = {}
    for service_type in ServiceType:
        total_usage = sum((metrics.services_used.get(service_type, 0) for metrics in self.gke_team_metrics.values()))
        usage_patterns[service_type.value] = {'total_usage': total_usage, 'teams_using': sum((1 for metrics in self.gke_team_metrics.values() if metrics.services_used.get(service_type, 0) > 0)), 'average_usage_per_team': total_usage / max(1, len(self.gke_team_metrics))}
    return usage_patterns

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

