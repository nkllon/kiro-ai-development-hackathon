from src.rm_ddd.core.health import ModuleHealth

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'cli_project_commands',
            'cli_analysis_commands'
        ]
    