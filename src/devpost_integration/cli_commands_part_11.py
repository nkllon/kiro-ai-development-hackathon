
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project"""
        return self.project_commands.delete_project(project_id)
    
    # ReflectiveModule interface implementation