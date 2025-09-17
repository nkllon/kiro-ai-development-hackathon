from src.rm_ddd.core.health import ModuleHealth

def connect_to_devpost(self, project_id: str, hackathon_id: str) -> ProjectConnection:
    """Connect local project to Devpost submission.
        
        Args:
            project_id: Devpost project ID
            hackathon_id: Hackathon ID
            
        Returns:
            ProjectConnection instance
            
        Raises:
            ConfigurationError: If connection setup fails
        """
    try:
        config = DevpostConfig(project_id=project_id, hackathon_id=hackathon_id, sync_enabled=True, watch_patterns=['README*', '*.md', 'package.json', 'pyproject.toml', 'media/*'], sync_interval=300, auto_sync_media=True, notification_enabled=True)
        connection = ProjectConnection(local_path=self.project_root, devpost_project_id=project_id, hackathon_id=hackathon_id, sync_status=SyncStatus.PENDING, configuration=config, created_at=datetime.now())
        self.config_manager.save_connection(connection)
        self._current_connection = connection
        return connection
    except Exception as e:
        raise ConfigurationError(f'Failed to connect to Devpost project: {e}')

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

