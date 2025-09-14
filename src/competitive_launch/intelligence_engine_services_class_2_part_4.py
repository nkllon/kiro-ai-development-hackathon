from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        register_module(self.__class__.__name__, self)
        """Initialize competitive intelligence engine."""
        self.competitors = ['Meta', 'Google', 'Microsoft', 'OpenAI', 'Anthropic']
        self.monitoring_active = False
        self.last_analysis = None
        logger.info('Competitive Intelligence Engine initialized')
