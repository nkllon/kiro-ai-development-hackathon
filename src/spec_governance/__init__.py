"""
Spec Governance Module

Provides systematic validation, remediation, and lifecycle management
for all specifications in .kiro/specs/ directory.
"""

from .validator import SpecValidator
from .reporter import SpecReporter
from .remediator import SpecRemediator
from .registry import SpecRegistry

__version__ = "1.0.0"
__all__ = ["SpecValidator", "SpecReporter", "SpecRemediator", "SpecRegistry"]
