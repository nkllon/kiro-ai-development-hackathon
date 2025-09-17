from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def validate_path_consistency(paths: List[Union[str, Path]], base: Optional[Union[str, Path]]=None) -> bool:
        """
        Validate that a list of paths can be handled consistently.
        
        This method checks if all paths in a list can be normalized and optionally
        made relative to a base directory without conflicts.
        
        Args:
            paths: List of paths to validate
            base: Optional base directory for relative path validation
            
        Returns:
            bool: True if all paths can be handled consistently
            
        Example:
            >>> paths = ["src/main.py", "tests/test.py", "docs/readme.md"]
            >>> PathNormalizer.validate_path_consistency(paths, "/project/root")
            True
        """
        try:
            normalized_paths = []
            for path in paths:
                normalized = PathNormalizer.normalize_path(path)
                normalized_paths.append(normalized)
                if base is not None:
                    PathNormalizer.ensure_relative_to(path, base)
            if len(set(normalized_paths)) != len(normalized_paths):
                return False
            return True
        except (ValueError, OSError):
            return False


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