
    def create_project(self, title: str, description: str, technologies: List[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new project"""
        return self.project_commands.create_project(title, description, technologies, tags)
    