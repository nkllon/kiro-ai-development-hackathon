from src.rm_ddd.core.registry import register_module

    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Enhanced interface registration with proactive checks"""
        # Run proactive checks before registration
        health_check = self.run_interface_health_check(interface)
        
        if health_check.health_score < 0.7:
            print(f"⚠️  Interface health score below threshold: {health_check.health_score}")
            for issue in health_check.issues:
                print(f"   - {issue}")
            for recommendation in health_check.recommendations:
                print(f"   - {recommendation}")
        
        # Check for potential duplicates using rules
        duplicate_warnings = self.check_duplicate_prevention_rules(interface)
        for warning in duplicate_warnings:
            print(f"⚠️  {warning}")
        
        # Proceed with registration
        success = super().register_interface(interface)
        if success:
            self.health_checks[interface.interface_id] = health_check
            self.save_health_checks()
        
        return success

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

    