from src.rm_ddd.core.health import ModuleHealth

class ValidatedashboardconfigClass:
    """Auto-generated class for functions."""

    def _validate_dashboard_config(self, config: DashboardConfig) -> bool:
    """Validate dashboard configuration"""
    if not config.dashboard_id or not config.title:
    return False
    if config.refresh_interval_seconds <= 0:
    return False
    if config.data_retention_hours <= 0:
    return False
    return True

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

