from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _is_documentation_file(self, file_path: Path) -> bool:
    """Check if file is a documentation file."""
    doc_patterns = ['readme', 'changelog', 'license', 'contributing', 'docs']
    filename_lower = file_path.name.lower()
    return any((pattern in filename_lower for pattern in doc_patterns)) or file_path.suffix.lower() in {'.md', '.txt', '.rst', '.adoc'} or 'docs/' in str(file_path).lower()

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

