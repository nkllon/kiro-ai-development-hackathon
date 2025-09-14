from src.rm_ddd.core.health import ModuleHealth

def _resolve_duplicate_hackathon_path(self, resolution: str, **kwargs) -> bool:
    """Resolve duplicate hackathon path conflict."""
    hackathon_id = kwargs.get('hackathon_id')
    path = kwargs.get('path')
    keep_project_id = kwargs.get('keep_project_id')
    if resolution == 'keep_one':
        if not all([hackathon_id, path, keep_project_id]):
            raise ConfigurationError('hackathon_id, path, and keep_project_id required')
        connections = self.config_manager.list_connections()
        for connection in connections:
            if connection.hackathon_id == hackathon_id and str(connection.local_path) == path and (connection.devpost_project_id != keep_project_id):
                self.config_manager.remove_connection(connection.local_path)
        return True
    return False
