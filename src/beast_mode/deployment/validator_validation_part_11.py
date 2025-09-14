from src.rm_ddd.core.health import ModuleHealth

class CheckdnsresolutionClass:
    """Auto-generated class for functions."""

    def _check_dns_resolution(self, hostname: str, name: str) -> ValidationResult:
    """Check DNS resolution"""
    start_time = time.time()
    try:
    socket.gethostbyname(hostname)
    duration_ms = (time.time() - start_time) * 1000
    return ValidationResult(name=name, passed=True, message=f'DNS resolution successful for {hostname}', duration_ms=duration_ms)
    except Exception as e:
    duration_ms = (time.time() - start_time) * 1000
    return ValidationResult(name=name, passed=False, message=f'DNS resolution failed for {hostname}: {str(e)}', duration_ms=duration_ms)

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

