
def __init__(self):
    """Initialize the global registry."""
    self._modules: Dict[str, RegisteredModule] = {}
    self._capabilities: Dict[str, List[str]] = {}
    self._lock = Lock()
    self._health_check_task: Optional[asyncio.Task] = None
    self._health_check_interval = timedelta(seconds=60)
    self._registry_id = str(uuid4())
    self._created_at = datetime.now()
    logger.info(f'GlobalRegistry initialized: {self._registry_id}')

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

