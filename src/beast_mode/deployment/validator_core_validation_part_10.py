from src.rm_ddd.core.health import ModuleHealth

class CheckportconnectivityClass:
    """Auto-generated class for functions."""

    def _check_port_connectivity(self, host: str, port: int, name: str) -> ValidationResult:
    """Check if a port is accessible"""
    start_time = time.time()
    try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    duration_ms = (time.time() - start_time) * 1000
    if result == 0:
    return ValidationResult(name=name, passed=True, message=f'Port {port} on {host} is accessible', duration_ms=duration_ms)
    else:
    return ValidationResult(name=name, passed=False, message=f'Port {port} on {host} is not accessible', duration_ms=duration_ms)
    except Exception as e:
    duration_ms = (time.time() - start_time) * 1000
    return ValidationResult(name=name, passed=False, message=f'Port connectivity check failed: {str(e)}', duration_ms=duration_ms)

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

