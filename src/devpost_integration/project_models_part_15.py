from src.rm_ddd.core.health import ModuleHealth

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'project_id': self.project_id, 'team_member_count': len(self.team_members), 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'has_deadline': self.submission_deadline is not None}
