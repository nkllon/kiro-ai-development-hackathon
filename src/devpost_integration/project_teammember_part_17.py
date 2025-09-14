from src.rm_ddd.core.health import ModuleHealth

    def update_member_data(self, updates: Dict[str, Any]) -> bool:
        """Update member data."""
        try:
            self.member_data.update(updates)
            if 'id' in updates:
                self.member_id = updates['id']
            if 'name' in updates:
                self.name = updates['name']
            if 'email' in updates:
                self.email = updates['email']
            if 'role' in updates:
                self.role = updates['role']
            if 'permissions' in updates:
                self.permissions = updates['permissions']
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update member data: {e}')
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

