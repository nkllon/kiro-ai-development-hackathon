from src.rm_ddd.core.health import ModuleHealth

def validate_project(self) -> bool:
    """Validate project data"""
    try:
        self._update_metrics('validate_project')
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in self.project_data or not self.project_data[field]:
                self._logger.warning(f'Missing required field: {field}')
                return False
        return True
    except Exception as e:
        self._logger.error(f'Project validation failed: {e}')
        self._metrics['error_count'] += 1
        return False

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

