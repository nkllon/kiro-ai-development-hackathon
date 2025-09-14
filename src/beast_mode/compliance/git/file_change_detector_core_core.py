import logging
from pathlib import Path
from typing import List, Dict, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from ...core.reflective_module import ReflectiveModule
from ..models import CommitInfo, FileChangeAnalysis
from ...utils.path_normalizer import PathNormalizer, normalize_path, safe_relative_to
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
import fnmatch
from .file_change_detector_core_core_core import *
from .file_change_detector_core_core_validation import *
from src.rm_ddd.core.health import ModuleHealth


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

