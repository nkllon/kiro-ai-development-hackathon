
def __init__(self, module: 'ReflectiveModuleBase'):
    """
        Initialize health monitor for a specific module.
        
        Args:
            module: The RM module to monitor
        """
    self.module = module
    self.module_id = module.module_id
    self._health_history: List[ModuleHealth] = []
    self._health_indicators: Dict[str, HealthIndicator] = {}
    self._monitoring_active = False
    self._monitoring_task: Optional[asyncio.Task] = None
    self._check_interval = timedelta(seconds=30)
    logger.info(f'HealthMonitor initialized for module: {self.module_id}')

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

