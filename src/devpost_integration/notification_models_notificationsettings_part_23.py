from src.rm_ddd.core.health import ModuleHealth

class GetsettingssummaryClass:
    """Auto-generated class for functions."""

    def get_settings_summary(self) -> Dict[str, Any]:
    """Get settings summary."""
    return {'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channels': self.channels, 'quiet_hours': self.quiet_hours}

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

