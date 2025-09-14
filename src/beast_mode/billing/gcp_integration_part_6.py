from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        if OPENFLOW_ASSETS_AVAILABLE:
            self.logger.info('Using OpenFlow asset bridge for GCP integration')
            self._init_openflow_bridge()
        else:
            self.logger.info('Using direct GCP SDK integration (fallback)')
            self._init_gcp_sdk_fallback()
        self.last_update = None
        self.cached_metrics = None
        self.cache_duration = timedelta(minutes=config.get('cache_duration_minutes', 15))
        self.health_status = HealthStatus(is_healthy=True, status_message='Initialized', last_check=datetime.now(), metrics={})

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

