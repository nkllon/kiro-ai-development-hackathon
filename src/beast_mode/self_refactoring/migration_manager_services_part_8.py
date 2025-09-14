from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if migration manager is healthy"""
        try:
            for state in self.migration_states.values():
                if state.migration_phase == 'failed':
                    return False
            if self.migration_states and (not self.rollback_snapshots):
                return False
            return True
        except Exception as e:
            self.logger.error(f'Migration manager health check failed: {e}')
            return False

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

