from src.rm_ddd.core.health import ModuleHealth

def get_project_summary(self) -> Dict[str, Any]:
    """Get project summary."""
    return {'project_id': self.project_id, 'title': self.title, 'description': self.description[:200] + '...' if len(self.description) > 200 else self.description, 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'team_member_count': len(self.team_members), 'submission_deadline': self.submission_deadline.isoformat() if self.submission_deadline else None}

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

