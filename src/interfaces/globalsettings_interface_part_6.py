from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, settings_data: Dict[str, Any]=None):
        """Initialize global settings."""
        super().__init__()
        self.module_id = 'global_settings'
        self.version = '1.0.0'
        self.settings_data = settings_data or self._get_default_settings()
        self._operation_count = 0
        self._errors = 0
        register_module(self)

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

