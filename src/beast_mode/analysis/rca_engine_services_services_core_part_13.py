from src.rm_ddd.core.health import ModuleHealth

def _analyze_configuration(self, failure: Failure) -> Dict[str, Any]:
    """Analyze configuration issues"""
    config_analysis = {}
    config_files = ['.env', 'config.json', 'settings.py', 'Makefile']
    for config_file in config_files:
        config_analysis[f'{config_file}_exists'] = Path(config_file).exists()
    return config_analysis

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

