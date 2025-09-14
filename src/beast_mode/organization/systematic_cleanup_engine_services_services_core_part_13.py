from src.rm_ddd.core.health import ModuleHealth

class CategorizefilessummaryClass:
    """Auto-generated class for functions."""

    def _categorize_files_summary(self, file_analyses: List[FileAnalysis]) -> Dict[str, int]:
    """Summarize files by category"""
    summary = {}
    for analysis in file_analyses:
    category = analysis.category.value
    summary[category] = summary.get(category, 0) + 1
    return summary

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

