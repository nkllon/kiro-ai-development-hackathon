from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

class ParsetestnameClass:
    """Auto-generated class for functions."""

    def _parse_test_name(self, test_name: str) -> Tuple[str, str, Optional[str]]:
    """Parse pytest node ID to extract file, function, and class"""
    try:
    parts = test_name.split('::')
    test_file = parts[0] if parts else 'unknown'
    test_function = 'unknown'
    test_class = None
    if len(parts) >= 2:
    if len(parts) == 2:
    test_function = parts[1]
    elif len(parts) == 3:
    test_class = parts[1]
    test_function = parts[2]
    return (test_file, test_function, test_class)
    except Exception as e:
    self.logger.error(f'Test name parsing failed: {e}')
    return ('unknown', 'unknown', None)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

    def register_module(self, registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
    registry.register(self.get_interface_metadata())

    def health_check(self):
    """Perform health check."""
    return {
    'status': 'healthy',
    'timestamp': datetime.now().isoformat(),
    'module_id': getattr(self, 'module_id', self.__class__.__name__)
    }

    def get_health_status(self):
    """Get current health status."""
    return self.health_check()

