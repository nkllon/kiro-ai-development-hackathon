from src.rm_ddd.core.health import ModuleHealth

def _calculate_overall_systematic_compliance(self) -> Dict[str, Any]:
    """Calculate overall systematic compliance metrics"""
    if not self.tool_metrics:
        return {'compliance_rate': 1.0, 'message': 'No metrics available'}
    total_compliance = sum((metrics.systematic_compliance_rate for metrics in self.tool_metrics.values()))
    average_compliance = total_compliance / len(self.tool_metrics)
    return {'overall_compliance_rate': average_compliance, 'compliant_tools': len(self.tool_metrics), 'total_tools': len(self.tool_metrics)}

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

