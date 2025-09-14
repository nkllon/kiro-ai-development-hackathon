from src.rm_ddd.core.health import ModuleHealth

def remove_team_member(self, member_id: str) -> bool:
    """Remove team member from project."""
    try:
        self.team_members = [m for m in self.team_members if m.get('id') != member_id]
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove team member: {e}')
        self._errors += 1
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

