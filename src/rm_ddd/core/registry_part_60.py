
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
