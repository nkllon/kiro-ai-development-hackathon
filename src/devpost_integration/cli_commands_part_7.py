from src.rm_ddd.core.health import ModuleHealth

    def interrogate_projects(self, verbose: bool = False, json_output: bool = False) -> Dict[str, Any]:
        """Interrogate all projects"""
        return self.analysis_commands.interrogate_projects(verbose, json_output)
    