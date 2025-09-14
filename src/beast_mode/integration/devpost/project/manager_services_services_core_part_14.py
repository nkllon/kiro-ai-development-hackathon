from src.rm_ddd.core.health import ModuleHealth

def switch_project(self, project_id: str) -> bool:
    """Switch to a different project context.
        
        Args:
            project_id: Devpost project ID to switch to
            
        Returns:
            True if switch was successful
            
        Raises:
            ConfigurationError: If project is not found or switch fails
        """
    connections = self.config_manager.list_connections()
    target_connection = None
    for connection in connections:
        if connection.devpost_project_id == project_id:
            target_connection = connection
            break
    if not target_connection:
        raise ConfigurationError(f'Project {project_id} not found')
    if not target_connection.local_path.exists():
        raise ConfigurationError(f'Project path {target_connection.local_path} no longer exists')
    self._current_connection = target_connection
    self._active_project_id = project_id
    return True
