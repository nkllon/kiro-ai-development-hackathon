from src.rm_ddd.core.health import ModuleHealth

def _select_gcp_services(self, component_type: str, requirements: List[str]) -> List[str]:
    """Select appropriate GCP services for component"""
    service_map = {'microservice': ['Cloud Run', 'Cloud Load Balancing', 'Cloud SQL'], 'data_pipeline': ['Cloud Dataflow', 'Cloud Storage', 'BigQuery'], 'api': ['Cloud Endpoints', 'Cloud Functions', 'Cloud CDN'], 'generic': ['Compute Engine', 'Cloud Storage', 'Cloud Monitoring']}
    return service_map.get(component_type, service_map['generic'])
