from src.rm_ddd.core.health import ModuleHealth

def _check_log_file_health(self, log_file: str) -> ValidationResult:
    """Check log file health"""
    start_time = time.time()
    try:
        if not os.path.exists(log_file):
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(name=f'Log file exists: {log_file}', passed=False, message=f'Log file does not exist: {log_file}', duration_ms=duration_ms)
        mtime = os.path.getmtime(log_file)
        age_seconds = time.time() - mtime
        duration_ms = (time.time() - start_time) * 1000
        if age_seconds < 3600:
            return ValidationResult(name=f'Log file activity: {log_file}', passed=True, message=f'Log file is active (last modified {age_seconds:.0f}s ago)', duration_ms=duration_ms, details={'age_seconds': age_seconds})
        else:
            return ValidationResult(name=f'Log file activity: {log_file}', passed=False, message=f'Log file may be stale (last modified {age_seconds:.0f}s ago)', duration_ms=duration_ms, details={'age_seconds': age_seconds})
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return ValidationResult(name=f'Log file health: {log_file}', passed=False, message=f'Log file check failed: {str(e)}', duration_ms=duration_ms)

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

