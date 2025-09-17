from src.rm_ddd.core.registry import register_module
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
