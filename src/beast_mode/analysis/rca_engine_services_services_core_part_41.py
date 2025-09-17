from src.rm_ddd.core.health import ModuleHealth

def _analyze_system_configuration(self, failure: Failure) -> Dict[str, Any]:
    """Analyze system configuration for infrastructure failures"""
    sys_config = {}
    try:
        sys_config['platform'] = os.uname().sysname
        sys_config['user'] = os.environ.get('USER', 'unknown')
        sys_config['home_set'] = 'HOME' in os.environ
        sys_config['path_set'] = 'PATH' in os.environ
    except Exception as e:
        sys_config['analysis_error'] = str(e)
    return sys_config

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

