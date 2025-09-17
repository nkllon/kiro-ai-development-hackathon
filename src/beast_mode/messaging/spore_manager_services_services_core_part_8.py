from src.rm_ddd.core.health import ModuleHealth

def get_spore_versions(self, spore_name: str) -> List[str]:
    """
        Get all versions of a spore
        
        Args:
            spore_name: Name of the spore
            
        Returns:
            List of version identifiers
        """
    versions = []
    try:
        version_pattern = f'{spore_name}_v*'
        for version_dir in self.versions_dir.glob(version_pattern):
            if version_dir.is_dir():
                versions.append(version_dir.name)
        versions.sort(reverse=True)
    except Exception as e:
        logger.error(f'Failed to get versions for {spore_name}: {e}')
    return versions

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

