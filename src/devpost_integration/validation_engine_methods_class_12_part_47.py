
def __init__(self) -> Any:
    """Initialize validation issue"""
    super().__init__(module_id='validationissue', version='1.0.0')
    register_module(self)
    self._logger = logging.getLogger(f'{__name__}.ValidationIssue')
    self._logger.info('ValidationIssue initialized with RM-DDD compliance')
