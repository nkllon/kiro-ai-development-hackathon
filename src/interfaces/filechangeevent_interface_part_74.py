from src.rm_ddd.core.health import ModuleHealth

def __init__(self, result_data: Dict[str, Any]=None):
    """Initialize sync result."""
    super().__init__()
    self.module_id = 'sync_result'
    self.version = '1.0.0'
    self.result_data = result_data or {}
    self.success = True
    self.error_message = None
    self.sync_time = datetime.now()
    self.records_processed = 0
    self.records_failed = 0
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

