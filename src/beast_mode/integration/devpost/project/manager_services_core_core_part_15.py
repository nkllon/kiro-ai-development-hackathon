from src.rm_ddd.core.health import ModuleHealth

def get_project_status(self, project_id: Optional[str]=None) -> Dict[str, Any]:
    """Get detailed status for a project.
        
        Args:
            project_id: Project ID to get status for. If None, uses current project.
            
        Returns:
            Dictionary with project status information
            
        Raises:
            ConfigurationError: If project is not found
        """
    if project_id:
        connections = self.config_manager.list_connections()
        target_connection = None
        for connection in connections:
            if connection.devpost_project_id == project_id:
                target_connection = connection
                break
        if not target_connection:
            raise ConfigurationError(f'Project {project_id} not found')
    else:
        if not self._current_connection:
            raise ConfigurationError('No active project')
        target_connection = self._current_connection
    original_connection = self._current_connection
    original_project_id = self._active_project_id
    try:
        self._current_connection = target_connection
        self._active_project_id = target_connection.devpost_project_id
        metadata = self.get_project_metadata()
        validation = self.validate_project()
        status = {'project_id': target_connection.devpost_project_id, 'hackathon_id': target_connection.hackathon_id, 'local_path': str(target_connection.local_path), 'sync_status': target_connection.sync_status.value, 'last_sync': target_connection.last_sync.isoformat() if target_connection.last_sync else None, 'created_at': target_connection.created_at.isoformat(), 'is_active': target_connection.devpost_project_id == original_project_id, 'configuration': target_connection.configuration.model_dump(), 'metadata': metadata.model_dump(), 'validation': {'is_valid': validation.is_valid, 'missing_fields': validation.missing_fields, 'validation_errors': validation.validation_errors, 'warnings': validation.warnings}, 'path_exists': target_connection.local_path.exists()}
        return status
    finally:
        self._current_connection = original_connection
        self._active_project_id = original_project_id

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

