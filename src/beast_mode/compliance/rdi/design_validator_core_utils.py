"""
Design Validator Core Utils

This module was extracted from design_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from src.rm_ddd.core.health import ModuleHealth


def _is_utility_component(self, impl_comp: ImplementationComponent) -> bool:
    """
        Check if an implementation component is a utility component that doesn't need design specification.
        
        Args:
            impl_comp: Implementation component to check
            
        Returns:
            True if it's a utility component
        """
    if impl_comp.name.startswith('_'):
        return True
    utility_names = {'main', 'setup', 'teardown', 'helper', 'util', 'test_'}
    if any((util in impl_comp.name.lower() for util in utility_names)):
        return True
    if impl_comp.name.startswith('test_') or 'test' in impl_comp.file_path.lower():
        return True
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

