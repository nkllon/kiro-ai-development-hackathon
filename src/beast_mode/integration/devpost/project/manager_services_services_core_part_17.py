
def detect_project_conflicts(self) -> List[Dict[str, Any]]:
    """Detect conflicts between projects.
        
        Returns:
            List of conflict descriptions
        """
    connections = self.config_manager.list_connections()
    conflicts = []
    project_ids = {}
    for connection in connections:
        project_id = connection.devpost_project_id
        if project_id in project_ids:
            conflicts.append({'type': 'duplicate_project_id', 'project_id': project_id, 'paths': [str(project_ids[project_id]), str(connection.local_path)], 'description': f'Project ID {project_id} is connected to multiple local paths'})
        else:
            project_ids[project_id] = connection.local_path
    hackathon_paths = {}
    for connection in connections:
        hackathon_id = connection.hackathon_id
        path_str = str(connection.local_path)
        if hackathon_id in hackathon_paths:
            if path_str in hackathon_paths[hackathon_id]:
                conflicts.append({'type': 'duplicate_hackathon_path', 'hackathon_id': hackathon_id, 'path': path_str, 'project_ids': hackathon_paths[hackathon_id][path_str], 'description': f'Multiple projects for hackathon {hackathon_id} at path {path_str}'})
            else:
                hackathon_paths[hackathon_id][path_str] = [connection.devpost_project_id]
        else:
            hackathon_paths[hackathon_id] = {path_str: [connection.devpost_project_id]}
    for connection in connections:
        if not connection.local_path.exists():
            conflicts.append({'type': 'missing_path', 'project_id': connection.devpost_project_id, 'path': str(connection.local_path), 'description': f'Project path {connection.local_path} no longer exists'})
    return conflicts
