import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import ModuleStatus, ModuleCapability, DomainBoundaries, AggregateBoundaries, EntityId, AggregateId, DomainException, InvariantViolationException
from ..core.health import ModuleHealth
from .entities_core import *
from .entities_validation import *
from .entities_models import *

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

