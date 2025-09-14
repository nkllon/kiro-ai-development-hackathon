from src.rm_ddd.core.health import ModuleHealth

def __init__(self, preview_data: Dict[str, Any]=None):
    """Initialize preview data with comprehensive functionality"""
    super().__init__(module_id='previewdata', version='1.0.0')
    register_module(self)
    self._logger = logging.getLogger(f'{__name__}.PreviewData')
    self.preview_data = preview_data or self._get_default_preview_data()
    self.preview_id = self.preview_data.get('preview_id', self._generate_preview_id())
    self.created_at = datetime.now()
    self.updated_at = datetime.now()
    self.version = '1.0.0'
    self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'previews_generated': 0, 'preview_errors': 0}
    self._logger.info(f'PreviewData {self.preview_id} initialized with RM-DDD compliance')
