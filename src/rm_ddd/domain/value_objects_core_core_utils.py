"""
Value Objects Core Core Utils

This module was extracted from value_objects_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal
from datetime import datetime, date
import re
from ..core.compliance import ValidationResult
from ..models import DomainException, ValidationException
from src.rm_ddd.core.health import ModuleHealth


def get_formatted_address(self) -> str:
    """Get formatted address string."""
    parts = [self.street, self.city]
    if self.state:
        parts.append(self.state)
    if self.postal_code:
        parts.append(self.postal_code)
    parts.append(self.country)
    return ', '.join(parts)

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

