
def get_project_summary(self) -> Dict[str, Any]:
    """Get project summary."""
    return {'project_id': self.project_id, 'title': self.title, 'description': self.description[:200] + '...' if len(self.description) > 200 else self.description, 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'team_member_count': len(self.team_members), 'submission_deadline': self.submission_deadline.isoformat() if self.submission_deadline else None}
