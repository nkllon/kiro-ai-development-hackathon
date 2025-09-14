
    def get_project_status(self, project_id: str = None, json_output: bool = False) -> Dict[str, Any]:
        """Get project status"""
        return self.analysis_commands.get_project_status(project_id, json_output)
    