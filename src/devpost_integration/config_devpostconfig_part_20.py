from src.rm_ddd.core.health import ModuleHealth

class ValidateconfigurationClass:
    """Auto-generated class for functions."""

    def validate_configuration(self) -> bool:
    """Validate configuration values."""
    try:
    required_keys = ['api_base_url', 'api_version', 'timeout_seconds']
    for key in required_keys:
    if key not in self.config_data:
    return False
    timeout = self.config_data.get('timeout_seconds', 0)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
    return False
    return True
    except Exception as e:
    logger.error(f'Configuration validation failed: {e}')
    self._errors += 1
    return False

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

