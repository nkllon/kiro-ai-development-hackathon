"""
Build Core Core Validation

This module was extracted from build_core_core.py
as part of RM-DDD compliance refactoring.
"""

import json
from typing import List, Dict, Any, Optional
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
    return 'build_systems_detected' in result.metadata
    return True

    def _check_missing_build_files(self, directory: Path) -> List[Finding]:
    """Check for missing essential build files"""
    findings = []
    python_files = list(directory.rglob('*.py'))
    if python_files and (not any(((directory / f).exists() for f in ['requirements.txt', 'pyproject.toml', 'setup.py']))):
    findings.append(Finding(type=FindingType.BUILD_FAILURE, severity=Severity.MEDIUM, location=CodeLocation(str(directory), 1), description='Python project missing dependency file (requirements.txt, pyproject.toml, or setup.py)', confidence=0.8, evidence={'project_type': 'python', 'missing_files': ['requirements.txt', 'pyproject.toml', 'setup.py']}))
    js_files = list(directory.rglob('*.js')) + list(directory.rglob('*.ts'))
    if js_files and (not (directory / 'package.json').exists()):
    findings.append(Finding(type=FindingType.BUILD_FAILURE, severity=Severity.MEDIUM, location=CodeLocation(str(directory), 1), description='JavaScript/TypeScript project missing package.json', confidence=0.8, evidence={'project_type': 'javascript', 'missing_files': ['package.json']}))
    return findings

    def _check_build_conflicts(self, directory: Path) -> List[Finding]:
    """Check for conflicting build systems"""
    findings = []
    python_files = []
    for f in ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']:
    if (directory / f).exists():
    python_files.append(f)
    if len(python_files) > 2:
    findings.append(Finding(type=FindingType.BUILD_FAILURE, severity=Severity.LOW, location=CodeLocation(str(directory), 1), description=f"Multiple Python dependency files detected: {', '.join(python_files)}", confidence=0.7, evidence={'conflict_type': 'python_dependencies', 'files': python_files}))
    return findings

    def _check_dependency_versions(self, dependencies: Dict[str, str], file_path: Path, section: str) -> List[Finding]:
    """Check dependency versions for issues"""
    findings = []
    for dep_name, version in dependencies.items():
    if version in ['*', 'latest'] or version.startswith('^') or version.startswith('~'):
    findings.append(Finding(type=FindingType.DEPENDENCY_ISSUE, severity=Severity.LOW, location=CodeLocation(str(file_path), 1), description=f'Loose version constraint for {dep_name}: {version}', confidence=0.7, evidence={'dependency': dep_name, 'version': version, 'section': section}))
    return findings

    def _check_known_vulnerable_packages(self, dependencies: Dict[str, str], file_path: Path) -> List[Finding]:
    """Check for known vulnerable packages (simplified)"""
    findings = []
    known_vulnerable = {'lodash': ['4.17.15', '4.17.16'], 'moment': ['2.24.0']}
    for dep_name, version in dependencies.items():
    if dep_name in known_vulnerable:
    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), 1), description=f'Known vulnerable package: {dep_name}@{version}', confidence=0.6, evidence={'package': dep_name, 'version': version, 'vulnerability': 'known_vulnerable'}))
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

