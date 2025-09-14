
    def _initialize_registry_integration(cls):
        """Initialize registry integration at class level"""
        if hasattr(cls, '_registry_initialized'):
            return
        
        # Class-level introspection for registry integration
        cls._registry_initialized = True
        
        # Register class with interface registry
        from .interface_registry import InterfaceRegistry
        registry = InterfaceRegistry.get_instance()
        registry.register_class(cls)
        
        # Extract interface information
        interface_info = cls._extract_interface_info()
        registry.register_interface(cls.__name__, interface_info)
    
    @classmethod