
    def get_member_summary(self) -> Dict[str, Any]:
        """Get member summary."""
        return {'member_id': self.member_id, 'name': self.name, 'email': self.email, 'role': self.role, 'permissions': self.permissions}
