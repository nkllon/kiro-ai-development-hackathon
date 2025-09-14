from src.rm_ddd.core.health import ModuleHealth

def _get_compliance_metrics(self) -> Dict[str, Any]:
    """Get detailed compliance metrics"""
    return {'total_tools': len(self.registered_tools), 'compliant_tools': sum((1 for tool in self.registered_tools.values() if hasattr(tool, 'systematic_constraints'))), 'compliance_gaps': len(self.registered_tools) - sum((1 for tool in self.registered_tools.values() if hasattr(tool, 'systematic_constraints'))), 'systematic_compliance_rate': self.orchestration_metrics['systematic_compliance_rate']}

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

