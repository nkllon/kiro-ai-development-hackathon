from src.rm_ddd.core.health import ModuleHealth

    def __init__(self) -> Any:
        """Initialize link validation rule"""
        super().__init__(module_id='linkvalidationrule', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.LinkValidationRule')
        self._logger.info('LinkValidationRule initialized with RM-DDD compliance')
