from src.rm_ddd.core.health import ModuleHealth

def _get_default_settings(self) -> Dict[str, Any]:
    """Get default notification settings."""
    return {'enabled': True, 'timing': NotificationTiming.DAILY, 'channels': ['email'], 'quiet_hours': {'start': '22:00', 'end': '08:00'}, 'max_notifications_per_day': 10, 'digest_mode': True}

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

