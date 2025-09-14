
def __init__(self, config: DeploymentConfig):
    self.config = config
    self.logger = logging.getLogger(__name__)
    self.services: Dict[str, MonitoredService] = {}
    self.monitoring_thread: Optional[threading.Thread] = None
    self.running = False
    self.callbacks: Dict[str, List[Callable]] = {'service_started': [], 'service_stopped': [], 'service_failed': [], 'service_restarted': [], 'health_check_failed': []}
