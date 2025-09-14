from src.rm_ddd.core.health import ModuleHealth

def disconnect_project(self, project_id: str) -> bool:
    """Disconnect a project from Devpost integration.
        
        Args:
            project_id: Project ID to disconnect
            
        Returns:
            True if disconnection was successful
            
        Raises:
            ConfigurationError: If project is not found
        """
    connections = self.config_manager.list_connections()
    target_connection = None
    for connection in connections:
        if connection.devpost_project_id == project_id:
            target_connection = connection
            break
    if not target_connection:
        raise ConfigurationError(f'Project {project_id} not found')
    success = self.config_manager.remove_connection(target_connection.local_path)
    if self._active_project_id == project_id:
        self._current_connection = None
        self._active_project_id = None
    return success
