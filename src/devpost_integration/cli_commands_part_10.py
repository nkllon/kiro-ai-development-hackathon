
    def update_project(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing project"""
        return self.project_commands.update_project(project_id, **kwargs)
    