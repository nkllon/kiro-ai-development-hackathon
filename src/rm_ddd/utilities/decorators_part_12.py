from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class EnhancedinitClass:
    """Auto-generated class for functions."""

    def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)
    cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls
    return decorator

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

