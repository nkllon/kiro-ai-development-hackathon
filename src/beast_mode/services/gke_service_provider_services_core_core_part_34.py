from src.rm_ddd.core.health import ModuleHealth

def _estimate_resource_requirements(self, component_type: str, requirements: List[str]) -> Dict[str, Any]:
    """Estimate GCP resource requirements"""
    base_requirements = {'cpu': '2 vCPUs', 'memory': '4 GB', 'storage': '20 GB', 'network': 'Standard'}
    if 'high_performance' in requirements:
        base_requirements['cpu'] = '4 vCPUs'
        base_requirements['memory'] = '8 GB'
    if 'large_data' in requirements:
        base_requirements['storage'] = '100 GB'
    return base_requirements

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

