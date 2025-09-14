from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for security issues"""
        skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        if file_path.suffix.lower() in skip_extensions:
            return False
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            pass
        return True

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

