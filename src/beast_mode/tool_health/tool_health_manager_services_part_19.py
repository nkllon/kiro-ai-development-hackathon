from src.rm_ddd.core.health import ModuleHealth

    def _document_prevention_pattern(self, tool_name: str, diagnosis: ToolDiagnosis, repairs: List[str]) -> str:
        """Document pattern to prevent similar failures"""
        pattern = f'Tool: {tool_name}, Issues: {diagnosis.issues_found}, Repairs: {repairs}'
        return pattern

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

