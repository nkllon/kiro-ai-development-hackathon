from src.rm_ddd.core.health import ModuleHealth

class GetmodulestatusClass:
    """Auto-generated class for functions."""

    def get_module_status(self) -> Dict[str, Any]:
    """Dashboard manager operational status"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'total_dashboards': self.dashboard_metrics['total_dashboards'], 'active_dashboards': self.dashboard_metrics['active_dashboards'], 'data_points_collected': self.dashboard_metrics['data_points_collected'], 'last_update': self.dashboard_metrics['last_update_timestamp']}

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

