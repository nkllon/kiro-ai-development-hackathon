from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, api_key: str, base_url: str = "https://devpost.com"):
        super().__init__(module_id="api_client", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)
        
        self.api_key = api_key
        self.base_url = base_url
        self._error_count = 0
        self._command_count = 0

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

    