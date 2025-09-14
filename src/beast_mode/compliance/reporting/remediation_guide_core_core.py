from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from ..models import ComplianceAnalysisResult, ComplianceIssue, ComplianceIssueType, IssueSeverity, RemediationStep
from .remediation_guide_core_core_validation import *
from .remediation_guide_core_core_processing import *
from .remediation_guide_core_core_core import *
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

