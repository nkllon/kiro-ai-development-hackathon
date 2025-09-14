from src.rm_ddd.core.health import ModuleHealth

def _identify_health_issues(self) -> List[str]:
    """Identify health issues"""
    issues = []
    if self._metrics['success_rate'] < 0.8:
        issues.append('Low success rate detected')
    if self._metrics['error_count'] > 10:
        issues.append('High error count detected')
    if not self.preview_data.get('title'):
        issues.append('Preview title not set')
    if not self.preview_data.get('preview_url'):
        issues.append('Preview URL not set')
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

