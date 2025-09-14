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
