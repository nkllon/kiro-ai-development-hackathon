from src.rm_ddd.core.health import ModuleHealth

    def get_result_summary(self) -> Dict[str, Any]:
        """Get sync result summary."""
        return {'success': self.success, 'error_message': self.error_message, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed), 'sync_time': self.sync_time.isoformat()}

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

