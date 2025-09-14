from src.rm_ddd.core.health import ModuleHealth

    def create_project(self, title: str, description: str, technologies: List[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new project"""
        return self.project_commands.create_project(title, description, technologies, tags)

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

    