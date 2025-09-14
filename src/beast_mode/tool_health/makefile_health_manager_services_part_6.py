from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, metrics_engine: Optional[BaselineMetricsEngine]=None):
        super().__init__('makefile_health_manager')
        self.metrics_engine = metrics_engine
        self.diagnosis_count = 0
        self.repair_count = 0
        self.workarounds_rejected = 0
        self.repair_principles = {'no_workarounds': True, 'root_cause_only': True, 'systematic_validation': True, 'prevention_patterns': True}
        self.expected_makefile_modules = ['config.mk', 'platform.mk', 'colors.mk', 'quality.mk', 'activity-models.mk', 'domains.mk', 'testing.mk', 'installation.mk']
        self._update_health_indicator('makefile_diagnostic_readiness', HealthStatus.HEALTHY, 'ready', 'Makefile health diagnostics ready')

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

