
    def remove_permission(self, permission: str) -> bool:
        """Remove permission from member."""
        try:
            if permission in self.permissions:
                self.permissions.remove(permission)
                self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to remove permission: {e}')
            self._errors += 1
            return False
