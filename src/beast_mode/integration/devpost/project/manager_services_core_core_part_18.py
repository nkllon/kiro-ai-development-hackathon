from src.rm_ddd.core.health import ModuleHealth

def resolve_conflict(self, conflict_type: str, resolution: str, **kwargs) -> bool:
    """Resolve a detected conflict.
        
        Args:
            conflict_type: Type of conflict to resolve
            resolution: Resolution strategy
            **kwargs: Additional parameters for resolution
            
        Returns:
            True if conflict was resolved
            
        Raises:
            ConfigurationError: If resolution fails
        """
    try:
        if conflict_type == 'duplicate_project_id':
            return self._resolve_duplicate_project_id(resolution, **kwargs)
        elif conflict_type == 'duplicate_hackathon_path':
            return self._resolve_duplicate_hackathon_path(resolution, **kwargs)
        elif conflict_type == 'missing_path':
            return self._resolve_missing_path(resolution, **kwargs)
        else:
            raise ConfigurationError(f'Unknown conflict type: {conflict_type}')
    except Exception as e:
        raise ConfigurationError(f'Failed to resolve conflict: {e}')

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

