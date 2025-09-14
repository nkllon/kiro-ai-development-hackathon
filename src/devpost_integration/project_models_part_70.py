
def add_permission(self, permission: str) -> bool:
    """Add permission to member."""
    try:
        if permission not in self.permissions:
            self.permissions.append(permission)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add permission: {e}')
        self._errors += 1
        return False
