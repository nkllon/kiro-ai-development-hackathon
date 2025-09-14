from src.rm_ddd.core.health import ModuleHealth

    def _identify_health_issues(self) -> List[str]:
        """Identify specific health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Operation errors: {self._errors}')
        if self.status == 'failed':
            issues.append('Operation failed')
        if self.progress < 0 or self.progress > 1:
            issues.append(f'Invalid progress: {self.progress}')
        return issues

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

