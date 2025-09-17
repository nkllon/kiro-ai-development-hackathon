from src.rm_ddd.core.health import ModuleHealth

    def find_interface_by_name_and_type(self, name: str, interface_type: InterfaceType) -> Optional[InterfaceMetadata]:
        """Find interface by name and type"""
        for interface in self.interfaces.values():
            if (interface.interface_name == name and 
                interface.interface_type == interface_type and 
                interface.status != InterfaceStatus.DEPRECATED):
                return interface
        return None

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

    