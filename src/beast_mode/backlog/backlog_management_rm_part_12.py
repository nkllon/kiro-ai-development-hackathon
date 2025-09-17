from src.rm_ddd.core.health import ModuleHealth

    def create_backlog_item(self, item_spec: BacklogItemSpec) -> BacklogItem:
        """Create a new backlog item with validation"""
        return self._core_operations.create_backlog_item(item_spec, len(self._backlog_items))

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

            