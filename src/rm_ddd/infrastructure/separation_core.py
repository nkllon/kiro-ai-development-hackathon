import ast
import inspect
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
from datetime import datetime
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..models import DomainBoundaries
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries
from .separation_core_core import *
from .separation_core_validation import *

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

