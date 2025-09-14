from src.rm_ddd.core.health import ModuleHealth

class GetprojectconfigClass:
    """Auto-generated class for functions."""

    def get_project_config(self) -> DevpostConfig:
    """Get current project configuration.

    Returns:
    DevpostConfig instance

    Raises:
    ConfigurationError: If no configuration is found
    """
    if self._current_connection:
    return self._current_connection.configuration
    config = self.config_manager.load_config()
    if config:
    return config
    raise ConfigurationError('No project configuration found')

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

