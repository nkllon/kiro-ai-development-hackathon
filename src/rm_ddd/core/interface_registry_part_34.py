from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Register a new interface"""
        try:
            # Check for duplicates
            existing = self.find_interface_by_name_and_type(interface.interface_name, interface.interface_type)
            if existing and existing.status != InterfaceStatus.DEPRECATED:
                print(f"❌ DUPLICATE INTERFACE DETECTED!")
                print(f"   New: {interface.interface_name} ({interface.interface_type.value})")
                print(f"   Existing: {existing.interface_name} ({existing.interface_type.value})")
                print(f"   File: {existing.file_path}")
                return False
            
            # Register the interface
            self.interfaces[interface.interface_id] = interface
            
            # Update domain index
            for term in interface.domain_terms:
                if term not in self.domain_index:
                    self.domain_index[term] = set()
                self.domain_index[term].add(interface.interface_id)
            
            # Save registry
            self.save_registry()
            print(f"✅ Interface registered: {interface.interface_name}")
            return True
            
        except Exception as e:
            print(f"Error registering interface: {e}")
            return False
    