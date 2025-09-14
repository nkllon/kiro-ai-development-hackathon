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
