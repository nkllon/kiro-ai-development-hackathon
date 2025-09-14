from src.rm_ddd.core.registry import register_module

    def __init__(self):
        register_module(self.__class__.__name__, self)
        """Initialize the superiority engine."""
        self.metrics: List[SuperiorityMetric] = []
        self.evidence_packages: List[EvidencePackage] = []
        self.baseline_data = self._load_baseline_data()
        self._initialize_default_metrics()
        logger.info('Systematic Superiority Engine initialized')
