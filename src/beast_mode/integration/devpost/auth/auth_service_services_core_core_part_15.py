
def __init__(self):
    """Initialize DevPost auth service"""
    super().__init__(module_id='devpostauthservice', version='1.0.0')
    register_module(self)
    self._logger = logging.getLogger(f'{__name__}.DevpostAuthService')
    self._logger.info('DevpostAuthService initialized with RM-DDD compliance')
