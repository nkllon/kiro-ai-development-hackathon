
def list_projects(self) -> List[Dict[str, Any]]:
    """List all connected projects with their status.
        
        Returns:
            List of project information dictionaries
        """
    connections = self.config_manager.list_connections()
    projects = []
    for connection in connections:
        project_info = {'project_id': connection.devpost_project_id, 'hackathon_id': connection.hackathon_id, 'local_path': str(connection.local_path), 'sync_status': connection.sync_status.value, 'last_sync': connection.last_sync.isoformat() if connection.last_sync else None, 'created_at': connection.created_at.isoformat(), 'is_active': connection.devpost_project_id == self._active_project_id, 'sync_enabled': connection.configuration.sync_enabled}
        projects.append(project_info)
    return projects
