
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'member_id': self.member_id, 'role': self.role, 'permission_count': len(self.permissions)}
