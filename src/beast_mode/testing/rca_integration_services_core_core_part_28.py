from src.rm_ddd.core.health import ModuleHealth

class BuildsharedanalysiscontextClass:
    """Auto-generated class for functions."""

    def _build_shared_analysis_context(self, failures: List[TestFailureData], common_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build shared context for batch analysis"""
    return {'batch_analysis': True, 'batch_size': len(failures), 'common_patterns': common_patterns, 'failure_types': list(set((f.failure_type for f in failures))), 'affected_files': list(set((f.test_file for f in failures)))}

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

