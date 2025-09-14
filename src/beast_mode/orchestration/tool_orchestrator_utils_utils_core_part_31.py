from src.rm_ddd.core.health import ModuleHealth

def _get_compliance_metrics(self) -> Dict[str, Any]:
    """Get detailed compliance metrics"""
    return {'total_tools': len(self.registered_tools), 'compliant_tools': sum((1 for tool in self.registered_tools.values() if hasattr(tool, 'systematic_constraints'))), 'compliance_gaps': len(self.registered_tools) - sum((1 for tool in self.registered_tools.values() if hasattr(tool, 'systematic_constraints'))), 'systematic_compliance_rate': self.orchestration_metrics['systematic_compliance_rate']}
