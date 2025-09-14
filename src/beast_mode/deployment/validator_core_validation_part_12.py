from src.rm_ddd.core.health import ModuleHealth

class CheckprocessrunningClass:
    """Auto-generated class for functions."""

    def _check_process_running(self, process_name: str) -> ValidationResult:
    """Check if a process is running"""
    start_time = time.time()
    try:
    result = subprocess.run(['pgrep', '-f', process_name], capture_output=True, text=True)
    duration_ms = (time.time() - start_time) * 1000
    if result.returncode == 0:
    pids = result.stdout.strip().split('\n')
    return ValidationResult(name=f'Process running: {process_name}', passed=True, message=f"Process {process_name} is running (PIDs: {', '.join(pids)})", duration_ms=duration_ms, details={'pids': pids})
    else:
    return ValidationResult(name=f'Process running: {process_name}', passed=False, message=f'Process {process_name} is not running', duration_ms=duration_ms)
    except Exception as e:
    duration_ms = (time.time() - start_time) * 1000
    return ValidationResult(name=f'Process running: {process_name}', passed=False, message=f'Process check failed: {str(e)}', duration_ms=duration_ms)

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

