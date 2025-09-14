from src.rm_ddd.core.health import ModuleHealth

def validate_multi_project_config(self) -> bool:
    """Validate multi-project configuration"""
    try:
        self._update_metrics('validate_multi_project_config')
        if len(self.projects) > self.config_data.get('max_projects', 10):
            self._logger.warning('Project count exceeds maximum limit')
            return False
        for project_id, project_data in self.projects.items():
            if not project_data.get('config'):
                self._logger.warning(f'Project {project_id} has no configuration')
                return False
        self._logger.info('Multi-project configuration validation passed')
        return True
    except Exception as e:
        self._logger.error(f'Multi-project configuration validation failed: {e}')
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

