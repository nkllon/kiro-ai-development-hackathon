from src.rm_ddd.core.health import ModuleHealth

class GetmetricsClass:
    """Auto-generated class for functions."""

    def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'project_id': self.project_id, 'team_member_count': len(self.team_members), 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'has_deadline': self.submission_deadline is not None}

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

