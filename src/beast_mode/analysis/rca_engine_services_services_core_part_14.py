from src.rm_ddd.core.health import ModuleHealth

def _analyze_installation_integrity(self, failure: Failure) -> Dict[str, Any]:
    """Analyze installation integrity"""
    installation_analysis = {}
    try:
        installation_analysis['platform'] = os.uname().sysname
        installation_analysis['python_version'] = subprocess.run(['python3', '--version'], capture_output=True, text=True).stdout.strip()
    except Exception as e:
        installation_analysis['system_analysis_error'] = str(e)
    return installation_analysis

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

