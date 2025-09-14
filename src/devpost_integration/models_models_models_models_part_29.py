from src.rm_ddd.core.health import ModuleHealth

    def _get_default_preview_data(self) -> Dict[str, Any]:
        """Get default preview data"""
        return {'preview_id': self._generate_preview_id(), 'content_type': 'text', 'title': '', 'description': '', 'thumbnail_url': '', 'preview_url': '', 'metadata': {}, 'generated_at': datetime.now().isoformat(), 'expires_at': None, 'access_count': 0, 'status': 'active'}

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

