from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, project_manager):
        """Initialize CLI commands"""
        super().__init__(module_id="cli_commands", version="1.0.0")
        self.project_commands = CLIProjectCommands(project_manager)
        self.analysis_commands = CLIAnalysisCommands(project_manager)
        self._start_time = datetime.now()
        register_module(self)
    