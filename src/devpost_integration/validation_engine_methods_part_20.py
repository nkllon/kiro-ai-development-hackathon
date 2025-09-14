
    def __init__(self) -> Any:
        """Initialize validation rule"""
        super().__init__(module_id='validationrule', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.ValidationRule')
        self._logger.info('ValidationRule initialized with RM-DDD compliance')
