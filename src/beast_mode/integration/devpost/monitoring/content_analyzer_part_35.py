from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _calculate_content_hash(self, file_path: Path) -> Optional[str]:
    """Calculate SHA-256 hash of file content."""
    try:
        if not file_path.exists():
            return None
        if self._is_binary_file(file_path):
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
    except Exception as e:
        logger.error(f'Error calculating content hash for {file_path}: {e}')
        return None

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

