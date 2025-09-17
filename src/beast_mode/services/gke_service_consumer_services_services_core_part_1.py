from src.rm_ddd.core.health import ModuleHealth

def __init__(self):
    super().__init__('gke_service_consumer')
    self.pdca_orchestrator = PDCAOrchestrator()
    self.registry_intelligence = RegistryIntelligenceEngine()
    self.makefile_health_manager = MakefileHealthManager()
    self.test_suite = ComprehensiveTestSuite()
    self.active_requests = {}
    self.service_queue = []
    self.service_status = {ServiceType.PDCA_CYCLE: ServiceStatus.AVAILABLE, ServiceType.MODEL_DRIVEN_BUILDING: ServiceStatus.AVAILABLE, ServiceType.TOOL_HEALTH_MANAGEMENT: ServiceStatus.AVAILABLE, ServiceType.QUALITY_ASSURANCE: ServiceStatus.AVAILABLE}
    self.registered_teams = {}
    self.team_performance_metrics = {}
    self.service_metrics = {'total_requests': 0, 'successful_requests': 0, 'failed_requests': 0, 'average_response_time_ms': 0, 'gke_velocity_improvements': {}, 'service_usage_patterns': {}}
    self._update_health_indicator('gke_service_consumer', HealthStatus.HEALTHY, 'ready', 'GKE service consumer ready to serve teams')

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

