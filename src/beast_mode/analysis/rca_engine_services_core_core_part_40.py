from src.rm_ddd.core.health import ModuleHealth

def _analyze_make_targets(self, failure: Failure) -> Dict[str, Any]:
    """Analyze make target structure"""
    target_analysis = {}
    try:
        result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=5)
        target_analysis['make_help_available'] = result.returncode == 0
        if result.returncode == 0:
            target_analysis['available_targets'] = len(result.stdout.split('\n'))
        else:
            target_analysis['make_help_error'] = result.stderr
    except Exception as e:
        target_analysis['analysis_error'] = str(e)
    return target_analysis

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

