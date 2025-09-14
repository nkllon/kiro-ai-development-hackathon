from src.rm_ddd.core.health import ModuleHealth

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}

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

