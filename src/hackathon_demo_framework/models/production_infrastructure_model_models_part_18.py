from src.rm_ddd.core.health import ModuleHealth

    def _determine_deployment_status(self, health_metrics: Dict[str, Any], security_metrics: Dict[str, Any]) -> DeploymentStatus:
        """Determine deployment status based on metrics"""
        health_percentage = health_metrics['node_health']['health_percentage']
        security_score = security_metrics['compliance']['overall_score']
        if health_percentage >= 95 and security_score >= 90:
            return DeploymentStatus.HEALTHY
        elif health_percentage >= 80 and security_score >= 80:
            return DeploymentStatus.DEGRADED
        else:
            return DeploymentStatus.FAILED

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

