from src.rm_ddd.core.health import ModuleHealth

def add_consistency_check(self, check: ConsistencyCheck) -> None:
    """Add custom consistency check"""
    self._consistency_checks.append(check)
    self.logger.info(f'Added consistency check: {check.name}')

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

