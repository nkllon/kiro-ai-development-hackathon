from src.rm_ddd.core.health import ModuleHealth

    def __init__(self):
        super().__init__('ProductionInfrastructureModel', '1.0.0')
        self.model_registry = ModelRegistry()
        self.deployment_history: List[DeploymentResult] = []
        self.cost_optimization_history: List[CostOptimizationResult] = []
        self.security_validation_history: List[SecurityValidationResult] = []
        self.requirements_traceability = self._initialize_requirements_traceability()
        self.performance_metrics: List[Dict[str, Any]] = []
        self.optimization_savings: List[float] = []

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

