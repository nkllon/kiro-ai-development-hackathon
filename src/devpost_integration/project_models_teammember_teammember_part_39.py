
def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'member_id': self.member_id, 'name': self.name, 'role': self.role, 'permission_count': len(self.permissions)}
