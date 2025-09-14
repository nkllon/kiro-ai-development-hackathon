from src.rm_ddd.core.health import ModuleHealth

def _get_default_config(self) -> Dict[str, Any]:
    """Get default configuration values."""
    return {'api_base_url': 'https://devpost.com/api', 'api_version': 'v1', 'timeout_seconds': 30, 'retry_attempts': 3, 'debug_mode': False, 'auto_sync': True, 'sync_interval_minutes': 60}

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

