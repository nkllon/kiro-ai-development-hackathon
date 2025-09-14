from src.rm_ddd.core.health import ModuleHealth

def _resolve_duplicate_project_id(self, resolution: str, **kwargs) -> bool:
    """Resolve duplicate project ID conflict."""
    project_id = kwargs.get('project_id')
    keep_path = kwargs.get('keep_path')
    if resolution == 'keep_one':
        if not project_id or not keep_path:
            raise ConfigurationError('project_id and keep_path required for keep_one resolution')
        connections = self.config_manager.list_connections()
        for connection in connections:
            if connection.devpost_project_id == project_id and str(connection.local_path) != keep_path:
                self.config_manager.remove_connection(connection.local_path)
        return True
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

