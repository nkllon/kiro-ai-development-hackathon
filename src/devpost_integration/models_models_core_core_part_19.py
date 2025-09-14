from src.rm_ddd.core.health import ModuleHealth

def get_module_info(self) -> Dict[str, Any]:
    """Get module information"""
    return {'module_id': 'previewdata', 'version': '1.0.0', 'description': 'Preview data management and generation with comprehensive functionality', 'preview_id': self.preview_id, 'content_type': self.preview_data.get('content_type', 'text'), 'status': self.preview_data.get('status', 'active')}

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

