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
