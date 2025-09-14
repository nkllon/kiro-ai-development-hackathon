from src.rm_ddd.core.health import ModuleHealth

    def _get_oldest_data_age_hours(self) -> float:
        """Get age of oldest data in hours"""
        oldest_timestamp = None
        for history in self.data_history.values():
            if history:
                first_entry = min(history, key=lambda x: x.timestamp)
                if oldest_timestamp is None or first_entry.timestamp < oldest_timestamp:
                    oldest_timestamp = first_entry.timestamp
        if oldest_timestamp:
            age = datetime.now() - oldest_timestamp
            return age.total_seconds() / 3600
        return 0.0

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

