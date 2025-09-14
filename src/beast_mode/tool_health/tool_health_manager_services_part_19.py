from src.rm_ddd.core.health import ModuleHealth

    def _document_prevention_pattern(self, tool_name: str, diagnosis: ToolDiagnosis, repairs: List[str]) -> str:
        """Document pattern to prevent similar failures"""
        pattern = f'Tool: {tool_name}, Issues: {diagnosis.issues_found}, Repairs: {repairs}'
        return pattern
