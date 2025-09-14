from src.rm_ddd.core.health import ModuleHealth

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'project_id': self.project_id, 'title': self.title, 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'team_member_count': len(self.team_members)}
