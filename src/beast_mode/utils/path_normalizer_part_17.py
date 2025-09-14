from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def normalize_path(path: Union[str, Path]) -> Path:
        """
        Normalize path to consistent format.
        
        This method converts paths to absolute paths and resolves any symbolic links
        to ensure consistent path handling across the system.
        
        Args:
            path: Path to normalize (string or Path object)
            
        Returns:
            Path: Normalized absolute path
            
        Example:
            >>> PathNormalizer.normalize_path("src/main.py")
            PosixPath('/current/working/dir/src/main.py')
            
            >>> PathNormalizer.normalize_path("/absolute/path/file.py")
            PosixPath('/absolute/path/file.py')
        """
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj
        return path_obj.resolve()


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

    @staticmethod