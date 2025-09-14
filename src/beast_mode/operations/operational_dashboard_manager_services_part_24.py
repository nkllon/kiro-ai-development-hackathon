from src.rm_ddd.core.health import ModuleHealth

class UpdaterefreshmetricsClass:
    """Auto-generated class for functions."""

    def _update_refresh_metrics(self, refresh_time_ms: int):
    """Update dashboard refresh metrics"""
    current_avg = self.dashboard_metrics['average_refresh_time_ms']
    total_refreshes = self.dashboard_metrics.get('total_refreshes', 0) + 1
    new_avg = (current_avg * (total_refreshes - 1) + refresh_time_ms) / total_refreshes
    self.dashboard_metrics['average_refresh_time_ms'] = new_avg
    self.dashboard_metrics['total_refreshes'] = total_refreshes

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

