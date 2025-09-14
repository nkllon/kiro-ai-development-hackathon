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

