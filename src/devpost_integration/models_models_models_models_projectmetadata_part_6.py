from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, metadata: Dict[str, Any]=None):
        """Initialize project metadata with comprehensive functionality"""
        super().__init__(module_id='projectmetadata', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.ProjectMetadata')
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version = '1.0.0'
        self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'metadata_updates': 0}
        self._logger.info('ProjectMetadata initialized with RM-DDD compliance')

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

