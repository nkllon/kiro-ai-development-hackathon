from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, event_data: Dict[str, Any]=None):
        """Initialize file change event."""
        super().__init__()
        self.module_id = 'file_change_event'
        self.version = '1.0.0'
        self.event_data = event_data or {}
        self.file_path = self.event_data.get('file_path', '')
        change_type_value = self.event_data.get('change_type', ChangeType.MODIFIED)
        self.change_type = change_type_value if isinstance(change_type_value, ChangeType) else ChangeType(change_type_value)
        self.timestamp = datetime.now()
        self.file_size = self.event_data.get('file_size', 0)
        self.checksum = self.event_data.get('checksum', '')
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

