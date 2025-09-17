from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def get_logger_stats(self) -> Dict[str, Any]:
    """Get current logger statistics"""
    stats = self.stats.copy()
    if stats['start_time']:
        runtime = datetime.now() - stats['start_time']
        stats['runtime_seconds'] = runtime.total_seconds()
    stats.update({'is_running': self.is_running, 'is_connected': self.is_connected, 'current_log_file': str(self.current_log_file) if self.current_log_file else None, 'log_directory': str(self.log_directory), 'channel': self.channel})
    return stats

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

