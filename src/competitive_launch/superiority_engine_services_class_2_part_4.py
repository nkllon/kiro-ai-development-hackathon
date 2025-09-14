from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        register_module(self.__class__.__name__, self)
        """Initialize the superiority engine."""
        self.metrics: List[SuperiorityMetric] = []
        self.evidence_packages: List[EvidencePackage] = []
        self.baseline_data = self._load_baseline_data()
        self._initialize_default_metrics()
        logger.info('Systematic Superiority Engine initialized')

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

