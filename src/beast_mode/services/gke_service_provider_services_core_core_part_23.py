from src.rm_ddd.core.health import ModuleHealth

def _get_gcp_best_practices(self, component_type: str) -> List[str]:
    """Get GCP best practices for component type"""
    common_practices = ['Use IAM for access control', 'Implement proper logging and monitoring', 'Follow security best practices', 'Optimize for cost efficiency', 'Design for scalability']
    type_specific = {'microservice': ['Use Cloud Run for containerized services', 'Implement health checks', 'Use Cloud Load Balancing'], 'data_pipeline': ['Use Cloud Dataflow for stream processing', 'Implement data validation', 'Use Cloud Storage for data lake'], 'api': ['Use Cloud Endpoints for API management', 'Implement rate limiting', 'Use Cloud CDN for caching']}
    return common_practices + type_specific.get(component_type, [])
