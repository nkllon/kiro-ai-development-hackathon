from src.rm_ddd.core.health import ModuleHealth

    def start_sync(self, sync_data: Dict[str, Any]) -> bool:
        """Start synchronization operation."""
        try:
            self.sync_data = sync_data
            self.status = 'running'
            self.start_time = datetime.now()
            self.progress = 0.0
            self.error_message = None
            self._operation_count += 1
            self._update_metrics('start_sync')
            return True
        except Exception as e:
            logger.error(f'Failed to start sync: {e}')
            self._errors += 1
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

