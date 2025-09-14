import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from ..models import DevpostProject, ProjectMetadata, DevpostConfig, ProjectConnection, SyncStatus, ValidationResult
from ..interfaces import ProjectManagerInterface
from ..config import DevpostConfigManager
from ....core.exceptions import ConfigurationError, ValidationError
import tomllib
import tomli as tomllib
import tomllib
import tomli as tomllib
from .manager_core_core import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

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

