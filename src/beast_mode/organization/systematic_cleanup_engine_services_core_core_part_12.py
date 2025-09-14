from src.rm_ddd.core.health import ModuleHealth

def _calculate_entropy_metrics(self, file_analyses: List[FileAnalysis]) -> Dict[str, float]:
    """Calculate comprehensive entropy metrics"""
    total_files = len(file_analyses)
    if total_files == 0:
        return {'entropy_score': 0.0, 'organization_score': 1.0, 'systematic_compliance': 1.0}
    misplaced_files = len([f for f in file_analyses if f.recommended_location != 'root'])
    entropy_score = misplaced_files / total_files
    organization_score = 1.0 - entropy_score
    critical_issues = len([f for f in file_analyses if f.cleanup_priority == CleanupPriority.CRITICAL])
    systematic_compliance = max(0.0, 1.0 - critical_issues / total_files * 2)
    return {'entropy_score': entropy_score, 'organization_score': organization_score, 'systematic_compliance': systematic_compliance, 'total_files': total_files, 'misplaced_files': misplaced_files, 'critical_issues': critical_issues}

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

