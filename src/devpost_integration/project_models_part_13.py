
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_title_length': 200, 'max_description_length': 5000, 'max_team_members': 10, 'required_fields': ['project_id', 'title', 'description']}
