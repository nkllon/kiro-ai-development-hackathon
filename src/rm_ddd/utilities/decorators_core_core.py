import functools
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from ..core.compliance import ValidationResult
from ..models import DomainException, ValidationException, InvariantViolationException
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..domain.events import DomainEvent
from datetime import datetime
from datetime import datetime
from datetime import datetime
from datetime import datetime
from datetime import datetime
from datetime import datetime
from .decorators_core_core_validation import *
from .decorators_core_core_core import *
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

