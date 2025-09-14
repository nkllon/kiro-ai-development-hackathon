from src.rm_ddd.core.health import ModuleHealth

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}

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

