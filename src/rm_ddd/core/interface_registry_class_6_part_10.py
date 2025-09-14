from src.rm_ddd.core.health import ModuleHealth

    def find_interface_by_name_and_type(self, name: str, interface_type: InterfaceType) -> Optional[InterfaceMetadata]:
        """Find interface by name and type"""
        for interface in self.interfaces.values():
            if (interface.interface_name == name and 
                interface.interface_type == interface_type and 
                interface.status != InterfaceStatus.DEPRECATED):
                return interface
        return None
    