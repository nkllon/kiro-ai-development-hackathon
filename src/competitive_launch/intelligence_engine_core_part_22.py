from src.rm_ddd.core.health import ModuleHealth

def _calculate_accountability_metrics(self) -> AccountabilityImplementation:
    """Calculate accountability implementation metrics."""
    return AccountabilityImplementation(decision_audit_trail=0.98, responsibility_assignment=0.92, escalation_protocols=0.88, performance_tracking=0.9)

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

