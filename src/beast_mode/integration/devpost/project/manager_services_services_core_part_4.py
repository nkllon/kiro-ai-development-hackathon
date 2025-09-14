from src.rm_ddd.core.health import ModuleHealth

class UpdateconfigClass:
    """Auto-generated class for functions."""

    def update_config(self, updates: Dict[str, Any]) -> bool:
    """Update project configuration.

    Args:
    updates: Dictionary of configuration updates

    Returns:
    True if update was successful

    Raises:
    ConfigurationError: If update fails
    """
    try:
    current_config = self.get_project_config()
    config_dict = current_config.model_dump()
    config_dict.update(updates)
    updated_config = DevpostConfig(**config_dict)
    if self._current_connection:
    self._current_connection.configuration = updated_config
    self.config_manager.save_connection(self._current_connection)
    else:
    self.config_manager.save_config(updated_config)
    return True
    except Exception as e:
    raise ConfigurationError(f'Failed to update configuration: {e}')

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

