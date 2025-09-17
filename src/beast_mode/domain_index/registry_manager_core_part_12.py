from src.rm_ddd.core.health import ModuleHealth

def get_registry_stats(self) -> Dict[str, Any]:
    """Get comprehensive registry statistics"""
    return {'total_domains': len(self._domains), 'registry_loaded': self._registry_loaded, 'last_load_time': self._last_load_time.isoformat() if self._last_load_time else None, 'load_count': self.load_count, 'validation_count': self.validation_count, 'registry_path': str(self.registry_path), 'cache_stats': self._cache.get_stats(), 'index_stats': self._index.get_index_stats(), 'validation_stats': self._validator.get_validation_stats(), 'component_health': self.get_health_indicators()}

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

