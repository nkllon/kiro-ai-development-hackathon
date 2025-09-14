from src.rm_ddd.core.health import ModuleHealth

def _analyze_environmental_factors(self, failure: Failure) -> Dict[str, Any]:
    """Analyze environmental factors"""
    env_analysis = {}
    env_analysis['path_set'] = 'PATH' in os.environ
    env_analysis['home_set'] = 'HOME' in os.environ
    env_analysis['working_directory'] = os.getcwd()
    return env_analysis

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

