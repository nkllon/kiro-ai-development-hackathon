
    def has_permission(self, permission: str) -> bool:
        """Check if member has specific permission."""
        return permission in self.permissions
