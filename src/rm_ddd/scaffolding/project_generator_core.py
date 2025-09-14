import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
import jinja2
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from jinja2 import Template
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from jinja2 import Template
from jinja2 import Template
from .project_generator_core_core import *
from .project_generator_core_validation import *

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

