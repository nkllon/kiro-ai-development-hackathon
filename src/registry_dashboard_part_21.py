from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def main():
    """Main registry integration implementation."""
    print("🚀 Starting Registry Integration System...")
    print("Implementing registry integration for 11 modules...")
    
    system = RegistryIntegrationSystem()
    
    # Step 1: Scan for modules needing registry integration
    system.scan_modules_needing_registry()
    
    # Step 2: Implement registry integration
    system.implement_registry_integration()
    
    # Step 3: Create registry dashboard
    system.create_registry_dashboard()
    
    print(f"
✅ Registry integration complete!")
    print(f"Implemented registry integration in {len(system.modules_needing_registry)} modules")

if __name__ == "__main__":
    main()

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

