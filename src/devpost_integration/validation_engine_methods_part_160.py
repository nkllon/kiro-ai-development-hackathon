from src.rm_ddd.core.health import ModuleHealth

    def __init__(self) -> Any:
        """Initialize tag validation rule"""
        super().__init__(module_id='tagvalidationrule', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.TagValidationRule')
        self._logger.info('TagValidationRule initialized with RM-DDD compliance')
