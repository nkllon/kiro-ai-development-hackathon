from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """Get the current status of the git analyzer."""
        return {'module_name': 'GitAnalyzer', 'repository_path': str(self.repository_path), 'configuration': self._config, 'is_healthy': self.is_healthy()}

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

