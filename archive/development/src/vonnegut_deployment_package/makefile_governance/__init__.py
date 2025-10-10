"""
Makefile Syntax Repair and Governance System

A comprehensive system for validating, repairing, and governing Makefile syntax
and quality standards within the Beast Mode Framework.
"""

from .core.syntax_validator import MakefileSyntaxValidator
from .core.governance_engine import MakefileGovernanceEngine
from .core.health_monitor import MakefileHealthMonitor

__all__ = [
    'MakefileSyntaxValidator',
    'MakefileGovernanceEngine', 
    'MakefileHealthMonitor'
]