from src.rm_ddd.core.health import ModuleHealth

def __init__(self) -> Any:
    """Initialize team validation rule"""
    super().__init__(module_id='teamvalidationrule', version='1.0.0')
    register_module(self)
    self._logger = logging.getLogger(f'{__name__}.TeamValidationRule')
    self._logger.info('TeamValidationRule initialized with RM-DDD compliance')
