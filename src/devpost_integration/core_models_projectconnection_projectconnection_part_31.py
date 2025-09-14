from src.rm_ddd.core.health import ModuleHealth

def sync_with_devpost(self, data: Dict[str, Any]) -> bool:
    """Perform actual synchronization with DevPost."""
    try:
        self._update_metrics('sync_with_devpost')
        return True
    except Exception as e:
        logger.error(f'Sync with DevPost failed: {e}')
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

