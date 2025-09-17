from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if tool health manager is healthy"""
        try:
            if not self.repair_history:
                return True
            successful_repairs = len([r for r in self.repair_history if r.repair_successful])
            success_rate = successful_repairs / len(self.repair_history)
            return success_rate >= 0.7
        except Exception as e:
            self.logger.error(f'Tool health manager health check failed: {e}')
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

