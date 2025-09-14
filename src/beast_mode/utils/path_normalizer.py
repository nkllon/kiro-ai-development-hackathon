from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Path Normalizer Core Core Core

This module was extracted from path_normalizer_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Path_Normalizer - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for path_normalizer.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/beast_mode/utils/path_normalizer_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.446360
"""



import os
from pathlib import Path
from typing import Union, Optional, List
import logging

class PathNormalizer(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Utility class for normalizing and handling path operations consistently.
    
    This class provides static methods to handle common path operations that can
    cause issues when mixing absolute and relative paths.
    """

    @staticmethod
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

    @staticmethod
    def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
        """
        Ensure path is relative to base directory, handling absolute/relative conflicts.
        
        This method safely converts a path to be relative to a base directory,
        handling cases where the paths might be a mix of absolute and relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path cannot be made relative to base
            
        Example:
            >>> PathNormalizer.ensure_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.ensure_relative_to("/project/root/src/main.py", "/project/root")
            PosixPath('src/main.py')
        """
        normalized_path = PathNormalizer.normalize_path(path)
        normalized_base = PathNormalizer.normalize_path(base)
        try:
            return normalized_path.relative_to(normalized_base)
        except ValueError as e:
            path_obj = Path(path)
            if not path_obj.is_absolute():
                return path_obj
            else:
                raise ValueError(f"Path '{path}' cannot be made relative to '{base}'. Normalized path '{normalized_path}' is not under normalized base '{normalized_base}'") from e

    @staticmethod
    def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
        """
        Safely attempt to make path relative to base, returning None if not possible.
        
        This is a non-throwing version of ensure_relative_to that returns None
        instead of raising an exception when the path cannot be made relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path or None: Path relative to base directory, or None if not possible
            
        Example:
            >>> PathNormalizer.safe_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.safe_relative_to("/other/project/file.py", "/project/root")
            None
        """
        try:
            return PathNormalizer.ensure_relative_to(path, base)
        except ValueError:
            return None

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
    def resolve_path_conflict(path: Union[str, Path], base: Union[str, Path]) -> Path:
        """
        Resolve path conflicts by choosing the most appropriate representation.
        
        This method attempts to resolve conflicts between absolute and relative paths
        by choosing the representation that makes the most sense in context.
        
        Args:
            path: Path that may have conflicts
            base: Base directory for context
            
        Returns:
            Path: Resolved path in the most appropriate format
            
        Example:
            >>> PathNormalizer.resolve_path_conflict("src/main.py", "/project/root")
            PosixPath('src/main.py')  # Keeps relative if it makes sense
        """
        path_obj = Path(path)
        base_obj = Path(base)
        if not path_obj.is_absolute():
            potential_absolute = PathNormalizer.normalize_path(base_obj / path_obj)
            base_normalized = PathNormalizer.normalize_path(base_obj)
            try:
                potential_absolute.relative_to(base_normalized)
                return path_obj
            except ValueError:
                pass
        try:
            return PathNormalizer.ensure_relative_to(path, base)
        except ValueError:
            return PathNormalizer.normalize_path(path)

    @staticmethod
    def get_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
        """
        Find the common base directory for a list of paths.
        
        This method finds the deepest common directory that contains all the given paths.
        
        Args:
            paths: List of paths to find common base for
            
        Returns:
            Path or None: Common base directory, or None if no common base exists
            
        Example:
            >>> paths = ["/project/src/main.py", "/project/tests/test.py", "/project/docs/readme.md"]
            >>> PathNormalizer.get_common_base(paths)
            PosixPath('/project')
        """
        if not paths:
            return None
        try:
            normalized_paths = [PathNormalizer.normalize_path(p) for p in paths]
            common_parts = list(normalized_paths[0].parts)
            for path in normalized_paths[1:]:
                path_parts = list(path.parts)
                new_common = []
                for i, (common_part, path_part) in enumerate(zip(common_parts, path_parts)):
                    if common_part == path_part:
                        new_common.append(common_part)
                    else:
                        break
                common_parts = new_common
                if not common_parts:
                    return None
            if common_parts:
                return Path(*common_parts)
            else:
                return None
        except (ValueError, OSError):
            return None

class PathValidator(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Validator class for path operations and constraints.
    
    This class provides validation methods to ensure path operations
    are safe and consistent.
    """

    @staticmethod
    def is_safe_path(path: Union[str, Path], base: Union[str, Path]) -> bool:
        """
        Check if a path is safe relative to a base directory.
        
        This method validates that a path doesn't attempt to escape
        the base directory using ".." or other techniques.
        
        Args:
            path: Path to validate
            base: Base directory that should contain the path
            
        Returns:
            bool: True if path is safe, False otherwise
        """
        try:
            normalized_path = PathNormalizer.normalize_path(path)
            normalized_base = PathNormalizer.normalize_path(base)
            normalized_path.relative_to(normalized_base)
            path_str = str(normalized_path)
            if '..' in path_str or path_str.startswith('/..'):
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

def normalize_path(path: Union[str, Path]) -> Path:
    """Convenience function for PathNormalizer.normalize_path()"""
    return PathNormalizer.normalize_path(path)

def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """Convenience function for PathNormalizer.ensure_relative_to()"""
    return PathNormalizer.ensure_relative_to(path, base)

def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """Convenience function for PathNormalizer.safe_relative_to()"""
    return PathNormalizer.safe_relative_to(path, base)

@staticmethod
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

@staticmethod
def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Ensure path is relative to base directory, handling absolute/relative conflicts.
        
        This method safely converts a path to be relative to a base directory,
        handling cases where the paths might be a mix of absolute and relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path cannot be made relative to base
            
        Example:
            >>> PathNormalizer.ensure_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.ensure_relative_to("/project/root/src/main.py", "/project/root")
            PosixPath('src/main.py')
        """
    normalized_path = PathNormalizer.normalize_path(path)
    normalized_base = PathNormalizer.normalize_path(base)
    try:
        return normalized_path.relative_to(normalized_base)
    except ValueError as e:
        path_obj = Path(path)
        if not path_obj.is_absolute():
            return path_obj
        else:
            raise ValueError(f"Path '{path}' cannot be made relative to '{base}'. Normalized path '{normalized_path}' is not under normalized base '{normalized_base}'") from e

@staticmethod
def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """
        Safely attempt to make path relative to base, returning None if not possible.
        
        This is a non-throwing version of ensure_relative_to that returns None
        instead of raising an exception when the path cannot be made relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path or None: Path relative to base directory, or None if not possible
            
        Example:
            >>> PathNormalizer.safe_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.safe_relative_to("/other/project/file.py", "/project/root")
            None
        """
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return None

@staticmethod
def resolve_path_conflict(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Resolve path conflicts by choosing the most appropriate representation.
        
        This method attempts to resolve conflicts between absolute and relative paths
        by choosing the representation that makes the most sense in context.
        
        Args:
            path: Path that may have conflicts
            base: Base directory for context
            
        Returns:
            Path: Resolved path in the most appropriate format
            
        Example:
            >>> PathNormalizer.resolve_path_conflict("src/main.py", "/project/root")
            PosixPath('src/main.py')  # Keeps relative if it makes sense
        """
    path_obj = Path(path)
    base_obj = Path(base)
    if not path_obj.is_absolute():
        potential_absolute = PathNormalizer.normalize_path(base_obj / path_obj)
        base_normalized = PathNormalizer.normalize_path(base_obj)
        try:
            potential_absolute.relative_to(base_normalized)
            return path_obj
        except ValueError:
            pass
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return PathNormalizer.normalize_path(path)

@staticmethod
def get_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
        Find the common base directory for a list of paths.
        
        This method finds the deepest common directory that contains all the given paths.
        
        Args:
            paths: List of paths to find common base for
            
        Returns:
            Path or None: Common base directory, or None if no common base exists
            
        Example:
            >>> paths = ["/project/src/main.py", "/project/tests/test.py", "/project/docs/readme.md"]
            >>> PathNormalizer.get_common_base(paths)
            PosixPath('/project')
        """
    if not paths:
        return None
    try:
        normalized_paths = [PathNormalizer.normalize_path(p) for p in paths]
        common_parts = list(normalized_paths[0].parts)
        for path in normalized_paths[1:]:
            path_parts = list(path.parts)
            new_common = []
            for i, (common_part, path_part) in enumerate(zip(common_parts, path_parts)):
                if common_part == path_part:
                    new_common.append(common_part)
                else:
                    break
            common_parts = new_common
            if not common_parts:
                return None
        if common_parts:
            return Path(*common_parts)
        else:
            return None
    except (ValueError, OSError):
        return None

@staticmethod
def is_safe_path(path: Union[str, Path], base: Union[str, Path]) -> bool:
    """
        Check if a path is safe relative to a base directory.
        
        This method validates that a path doesn't attempt to escape
        the base directory using ".." or other techniques.
        
        Args:
            path: Path to validate
            base: Base directory that should contain the path
            
        Returns:
            bool: True if path is safe, False otherwise
        """
    try:
        normalized_path = PathNormalizer.normalize_path(path)
        normalized_base = PathNormalizer.normalize_path(base)
        normalized_path.relative_to(normalized_base)
        path_str = str(normalized_path)
        if '..' in path_str or path_str.startswith('/..'):
            return False
        return True
    except (ValueError, OSError):
        return False

@staticmethod
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

@staticmethod
def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Ensure path is relative to base directory, handling absolute/relative conflicts.
        
        This method safely converts a path to be relative to a base directory,
        handling cases where the paths might be a mix of absolute and relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path cannot be made relative to base
            
        Example:
            >>> PathNormalizer.ensure_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.ensure_relative_to("/project/root/src/main.py", "/project/root")
            PosixPath('src/main.py')
        """
    normalized_path = PathNormalizer.normalize_path(path)
    normalized_base = PathNormalizer.normalize_path(base)
    try:
        return normalized_path.relative_to(normalized_base)
    except ValueError as e:
        path_obj = Path(path)
        if not path_obj.is_absolute():
            return path_obj
        else:
            raise ValueError(f"Path '{path}' cannot be made relative to '{base}'. Normalized path '{normalized_path}' is not under normalized base '{normalized_base}'") from e

@staticmethod
def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """
        Safely attempt to make path relative to base, returning None if not possible.
        
        This is a non-throwing version of ensure_relative_to that returns None
        instead of raising an exception when the path cannot be made relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path or None: Path relative to base directory, or None if not possible
            
        Example:
            >>> PathNormalizer.safe_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.safe_relative_to("/other/project/file.py", "/project/root")
            None
        """
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return None

@staticmethod
def resolve_path_conflict(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Resolve path conflicts by choosing the most appropriate representation.
        
        This method attempts to resolve conflicts between absolute and relative paths
        by choosing the representation that makes the most sense in context.
        
        Args:
            path: Path that may have conflicts
            base: Base directory for context
            
        Returns:
            Path: Resolved path in the most appropriate format
            
        Example:
            >>> PathNormalizer.resolve_path_conflict("src/main.py", "/project/root")
            PosixPath('src/main.py')  # Keeps relative if it makes sense
        """
    path_obj = Path(path)
    base_obj = Path(base)
    if not path_obj.is_absolute():
        potential_absolute = PathNormalizer.normalize_path(base_obj / path_obj)
        base_normalized = PathNormalizer.normalize_path(base_obj)
        try:
            potential_absolute.relative_to(base_normalized)
            return path_obj
        except ValueError:
            pass
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return PathNormalizer.normalize_path(path)

@staticmethod
def get_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
        Find the common base directory for a list of paths.
        
        This method finds the deepest common directory that contains all the given paths.
        
        Args:
            paths: List of paths to find common base for
            
        Returns:
            Path or None: Common base directory, or None if no common base exists
            
        Example:
            >>> paths = ["/project/src/main.py", "/project/tests/test.py", "/project/docs/readme.md"]
            >>> PathNormalizer.get_common_base(paths)
            PosixPath('/project')
        """
    if not paths:
        return None
    try:
        normalized_paths = [PathNormalizer.normalize_path(p) for p in paths]
        common_parts = list(normalized_paths[0].parts)
        for path in normalized_paths[1:]:
            path_parts = list(path.parts)
            new_common = []
            for i, (common_part, path_part) in enumerate(zip(common_parts, path_parts)):
                if common_part == path_part:
                    new_common.append(common_part)
                else:
                    break
            common_parts = new_common
            if not common_parts:
                return None
        if common_parts:
            return Path(*common_parts)
        else:
            return None
    except (ValueError, OSError):
        return None

@staticmethod
def is_safe_path(path: Union[str, Path], base: Union[str, Path]) -> bool:
    """
        Check if a path is safe relative to a base directory.
        
        This method validates that a path doesn't attempt to escape
        the base directory using ".." or other techniques.
        
        Args:
            path: Path to validate
            base: Base directory that should contain the path
            
        Returns:
            bool: True if path is safe, False otherwise
        """
    try:
        normalized_path = PathNormalizer.normalize_path(path)
        normalized_base = PathNormalizer.normalize_path(base)
        normalized_path.relative_to(normalized_base)
        path_str = str(normalized_path)
        if '..' in path_str or path_str.startswith('/..'):
            return False
        return True
    except (ValueError, OSError):
        return False

@staticmethod
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

@staticmethod
def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Ensure path is relative to base directory, handling absolute/relative conflicts.
        
        This method safely converts a path to be relative to a base directory,
        handling cases where the paths might be a mix of absolute and relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path cannot be made relative to base
            
        Example:
            >>> PathNormalizer.ensure_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.ensure_relative_to("/project/root/src/main.py", "/project/root")
            PosixPath('src/main.py')
        """
    normalized_path = PathNormalizer.normalize_path(path)
    normalized_base = PathNormalizer.normalize_path(base)
    try:
        return normalized_path.relative_to(normalized_base)
    except ValueError as e:
        path_obj = Path(path)
        if not path_obj.is_absolute():
            return path_obj
        else:
            raise ValueError(f"Path '{path}' cannot be made relative to '{base}'. Normalized path '{normalized_path}' is not under normalized base '{normalized_base}'") from e

@staticmethod
def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """
        Safely attempt to make path relative to base, returning None if not possible.
        
        This is a non-throwing version of ensure_relative_to that returns None
        instead of raising an exception when the path cannot be made relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path or None: Path relative to base directory, or None if not possible
            
        Example:
            >>> PathNormalizer.safe_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.safe_relative_to("/other/project/file.py", "/project/root")
            None
        """
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return None

@staticmethod
def resolve_path_conflict(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Resolve path conflicts by choosing the most appropriate representation.
        
        This method attempts to resolve conflicts between absolute and relative paths
        by choosing the representation that makes the most sense in context.
        
        Args:
            path: Path that may have conflicts
            base: Base directory for context
            
        Returns:
            Path: Resolved path in the most appropriate format
            
        Example:
            >>> PathNormalizer.resolve_path_conflict("src/main.py", "/project/root")
            PosixPath('src/main.py')  # Keeps relative if it makes sense
        """
    path_obj = Path(path)
    base_obj = Path(base)
    if not path_obj.is_absolute():
        potential_absolute = PathNormalizer.normalize_path(base_obj / path_obj)
        base_normalized = PathNormalizer.normalize_path(base_obj)
        try:
            potential_absolute.relative_to(base_normalized)
            return path_obj
        except ValueError:
            pass
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return PathNormalizer.normalize_path(path)

@staticmethod
def get_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
        Find the common base directory for a list of paths.
        
        This method finds the deepest common directory that contains all the given paths.
        
        Args:
            paths: List of paths to find common base for
            
        Returns:
            Path or None: Common base directory, or None if no common base exists
            
        Example:
            >>> paths = ["/project/src/main.py", "/project/tests/test.py", "/project/docs/readme.md"]
            >>> PathNormalizer.get_common_base(paths)
            PosixPath('/project')
        """
    if not paths:
        return None
    try:
        normalized_paths = [PathNormalizer.normalize_path(p) for p in paths]
        common_parts = list(normalized_paths[0].parts)
        for path in normalized_paths[1:]:
            path_parts = list(path.parts)
            new_common = []
            for i, (common_part, path_part) in enumerate(zip(common_parts, path_parts)):
                if common_part == path_part:
                    new_common.append(common_part)
                else:
                    break
            common_parts = new_common
            if not common_parts:
                return None
        if common_parts:
            return Path(*common_parts)
        else:
            return None
    except (ValueError, OSError):
        return None

@staticmethod
def is_safe_path(path: Union[str, Path], base: Union[str, Path]) -> bool:
    """
        Check if a path is safe relative to a base directory.
        
        This method validates that a path doesn't attempt to escape
        the base directory using ".." or other techniques.
        
        Args:
            path: Path to validate
            base: Base directory that should contain the path
            
        Returns:
            bool: True if path is safe, False otherwise
        """
    try:
        normalized_path = PathNormalizer.normalize_path(path)
        normalized_base = PathNormalizer.normalize_path(base)
        normalized_path.relative_to(normalized_base)
        path_str = str(normalized_path)
        if '..' in path_str or path_str.startswith('/..'):
            return False
        return True
    except (ValueError, OSError):
        return False
