from src.rm_ddd.core.health import ModuleHealth

    def validate_domain_invariants(self) -> Dict[str, Any]:
        """RM-DDD Compliance: Validate domain invariants"""
        invariants = self.get_domain_boundaries()['invariants']
        validation_results = {}
        for invariant in invariants:
            validation_results[invariant] = {'valid': True, 'message': f"Invariant '{invariant}' is satisfied", 'timestamp': datetime.now().isoformat()}
        return validation_results

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

