from src.rm_ddd.core.health import ModuleHealth

def add_team_member(self, member_data: Dict[str, Any]) -> bool:
    """Add team member to project."""
    try:
        self.team_members.append(member_data)
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add team member: {e}')
        self._errors += 1
        return False
