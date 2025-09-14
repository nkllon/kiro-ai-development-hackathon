
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
