from src.rm_ddd.core.health import ModuleHealth

    def __init__(self) -> Any:
        """Initialize content quality rule"""
        super().__init__(module_id='contentqualityrule', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.ContentQualityRule')
        self._logger.info('ContentQualityRule initialized with RM-DDD compliance')
