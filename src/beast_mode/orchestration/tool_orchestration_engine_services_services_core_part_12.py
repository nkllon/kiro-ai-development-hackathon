from src.rm_ddd.core.health import ModuleHealth

def _execute_repair_procedure(self, tool_id: str, procedure: str) -> Dict[str, Any]:
    """
        Execute a specific repair procedure
        """
    try:
        result = subprocess.run(procedure.split(), capture_output=True, text=True, timeout=60, cwd=self.project_root)
        return {'success': result.returncode == 0, 'output': result.stdout, 'error': result.stderr, 'procedure': procedure}
    except Exception as e:
        return {'success': False, 'error': str(e), 'procedure': procedure}

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

