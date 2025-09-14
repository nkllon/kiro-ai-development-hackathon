"""
Path Normalizer Core Core Validation

This module was extracted from path_normalizer_core_core.py
as part of RM-DDD compliance refactoring.
"""

import os
from pathlib import Path
from typing import Union, Optional, List
import logging
from src.rm_ddd.core.health import ModuleHealth


@staticmethod
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

@staticmethod
def validate_file_extension(path: Union[str, Path], allowed_extensions: List[str]) -> bool:
    """
        Validate that a file has an allowed extension.
        
        Args:
            path: File path to validate
            allowed_extensions: List of allowed extensions (with or without dots)
            
        Returns:
            bool: True if extension is allowed, False otherwise
        """
    path_obj = Path(path)
    extension = path_obj.suffix.lower()
    normalized_extensions = []
    for ext in allowed_extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext.lower())
    return extension in normalized_extensions

@staticmethod
def validate_path_length(path: Union[str, Path], max_length: int=260) -> bool:
    """
        Validate that a path doesn't exceed maximum length.
        
        Args:
            path: Path to validate
            max_length: Maximum allowed path length (default 260 for Windows compatibility)
            
        Returns:
            bool: True if path length is acceptable, False otherwise
        """
    return len(str(path)) <= max_length

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

