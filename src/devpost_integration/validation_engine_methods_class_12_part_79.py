from src.rm_ddd.core.health import ModuleHealth

def __init__(self) -> Any:
    """Initialize required field rule"""
    super().__init__(module_id='requiredfieldrule', version='1.0.0')
    register_module(self)
    self._logger = logging.getLogger(f'{__name__}.RequiredFieldRule')
    self._logger.info('RequiredFieldRule initialized with RM-DDD compliance')
