from src.rm_ddd.core.health import ModuleHealth

def _get_component_health_summary(self) -> Dict[str, str]:
    """Get summary of component health status"""
    return {name: 'healthy' if metrics.is_healthy else 'unhealthy' for name, metrics in self.component_health.items()}
