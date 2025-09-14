from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, operation_id: str=None, operation_type: str='sync'):
        """Initialize sync operation with optional ID and type."""
        super().__init__()
        self.module_id = 'sync_operation'
        self.version = '1.0.0'
        self.operation_id = operation_id or self._generate_operation_id()
        self.operation_type = operation_type
        self.status = 'pending'
        self.progress = 0.0
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.sync_data = {}
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

