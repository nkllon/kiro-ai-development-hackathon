from src.rm_ddd.core.health import ModuleHealth

class SelectgcpservicesClass:
    """Auto-generated class for functions."""

    def _select_gcp_services(self, component_type: str, requirements: List[str]) -> List[str]:
    """Select appropriate GCP services for component"""
    service_map = {'microservice': ['Cloud Run', 'Cloud Load Balancing', 'Cloud SQL'], 'data_pipeline': ['Cloud Dataflow', 'Cloud Storage', 'BigQuery'], 'api': ['Cloud Endpoints', 'Cloud Functions', 'Cloud CDN'], 'generic': ['Compute Engine', 'Cloud Storage', 'Cloud Monitoring']}
    return service_map.get(component_type, service_map['generic'])

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

