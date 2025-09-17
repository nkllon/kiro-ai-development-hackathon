from src.rm_ddd.core.health import ModuleHealth

def _assess_cleanup_priority(self, file_path: Path, category: FileCategory) -> CleanupPriority:
    """Assess cleanup priority based on systematic impact"""
    name = file_path.name.lower()
    if category == FileCategory.TEMPORARY or name in ['.ds_store', '.coverage']:
        return CleanupPriority.CRITICAL
    if category in [FileCategory.DEVELOPMENT_ARTIFACT, FileCategory.UNKNOWN]:
        return CleanupPriority.HIGH
    if category in [FileCategory.SCRIPT, FileCategory.CONFIGURATION]:
        return CleanupPriority.MEDIUM
    return CleanupPriority.LOW

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

