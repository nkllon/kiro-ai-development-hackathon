from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _auto_register_entity(entity_instance: Any, domain_context: str):
    """Auto-register entity with bounded context."""
    try:
        logger.debug(f'Auto-registered entity {entity_instance.__class__.__name__} in context {domain_context}')
    except Exception as e:
        logger.warning(f'Failed to auto-register entity: {e}')

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

