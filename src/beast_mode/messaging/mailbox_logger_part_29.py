from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_log_files(self) -> List[Dict[str, Any]]:
    """Get information about all log files"""
    log_files = []
    try:
        for file_path in self.log_directory.glob('mailbox_*.log'):
            if file_path.is_file():
                stat = file_path.stat()
                log_files.append({'path': str(file_path), 'size_bytes': stat.st_size, 'size_mb': round(stat.st_size / (1024 * 1024), 2), 'created': datetime.fromtimestamp(stat.st_ctime).isoformat(), 'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(), 'is_current': file_path == self.current_log_file})
        log_files.sort(key=lambda x: x['created'], reverse=True)
    except Exception as e:
        logger.error(f'Error getting log file information: {e}')
    return log_files

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

