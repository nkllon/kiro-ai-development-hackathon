from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, validation_data: Dict[str, Any] = None):
        """Initialize validation result."""
        super().__init__()
        self.module_id = "validation_result"
        self.version = "1.0.0"
        self.validation_data = validation_data or {}
        self.errors = []
        self.warnings = []
        self.is_valid = True
        self.validation_time = datetime.now()
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

    