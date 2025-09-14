
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
