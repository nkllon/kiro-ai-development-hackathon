from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _initialize_log_file(self) -> None:
    """Initialize the current log file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
    try:
        self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
        logger.info(f'Initialized log file: {self.current_log_file}')
    except Exception as e:
        logger.error(f'Failed to initialize log file: {e}')
        raise

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

