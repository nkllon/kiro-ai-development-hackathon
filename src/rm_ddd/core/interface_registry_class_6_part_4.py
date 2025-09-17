
    def _initialize_registry_integration(cls):
        """Initialize registry integration at class level"""
        if hasattr(cls, '_registry_initialized'):
            return
        
        # Class-level introspection for registry integration
        cls._registry_initialized = True
        
        # Register class with interface registry
        from .interface_registry import InterfaceRegistry
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        registry = InterfaceRegistry.get_instance()
        registry.register_class(cls)
        
        # Extract interface information
        interface_info = cls._extract_interface_info()
        registry.register_interface(cls.__name__, interface_info)
    

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

    @classmethod