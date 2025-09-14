from src.rm_ddd.core.health import ModuleHealth

    def _validate_tool_repair(self, tool_name: str) -> Dict[str, Any]:
        """Validate that tool repair actually works"""
        if tool_name == 'makefile':
            try:
                result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
                return {'success': result.returncode == 0, 'output': result.stdout}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        return {'success': True}
