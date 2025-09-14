"""
Architecture Core Validation

This module was extracted from architecture_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import AnalysisResult, AnalysisContext, Finding, Recommendation, FindingType, Severity, CodeLocation
from src.rm_ddd.core.health import ModuleHealth


class ValidateconfidenceClass:
    """Auto-generated class for functions."""

    def validate_confidence(self, result: AnalysisResult) -> bool:
    """Validate confidence score accuracy"""
    if not 0.0 <= result.confidence <= 1.0:
    return False
    if result.confidence > 0.8:
    return 'complexity_metrics' in result.metadata
    return True

    def _check_solid_violations(self, content: str, file_path: Path) -> List[Finding]:
    """Check for SOLID principle violations"""
    findings = []
    if re.search('if\\s+isinstance\\s*\\(.*,\\s*\\w+\\)', content) or re.search('type\\s*\\(.*\\)\\s*==', content):
    findings.append(Finding(type=FindingType.ARCHITECTURE_VIOLATION, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), 1), description='Potential Open/Closed Principle violation - type checking detected', confidence=0.6, evidence={'solid_violation': 'ocp', 'issue': 'type_checking'}))
    if 'NotImplementedError' in content:
    findings.append(Finding(type=FindingType.ARCHITECTURE_VIOLATION, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), 1), description='Potential Liskov Substitution Principle violation - NotImplementedError found', confidence=0.7, evidence={'solid_violation': 'lsp', 'issue': 'not_implemented'}))
    concrete_import_pattern = 'from\\s+\\w+\\.\\w+\\.\\w+\\s+import\\s+\\w+'
    if re.search(concrete_import_pattern, content):
    findings.append(Finding(type=FindingType.ARCHITECTURE_VIOLATION, severity=Severity.LOW, location=CodeLocation(str(file_path), 1), description='Potential Dependency Inversion Principle violation - concrete imports detected', confidence=0.5, evidence={'solid_violation': 'dip', 'issue': 'concrete_imports'}))
    return findings

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

