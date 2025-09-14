"""
Security Core Core Validation

This module was extracted from security_core_core.py
as part of RM-DDD compliance refactoring.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import AnalysisResult, AnalysisContext, Finding, Recommendation, FindingType, Severity, CodeLocation
import stat
import stat
import stat

def validate_confidence(self, result: AnalysisResult) -> bool:
    """Validate confidence score accuracy"""
    if not 0.0 <= result.confidence <= 1.0:
        return False
    if result.confidence > 0.8:
        return 'security_checks_performed' in result.metadata
    if result.confidence < 0.3:
        return any((f.severity == Severity.CRITICAL for f in result.findings))
    return True

def _check_sql_injection(self, content: str, file_path: Path) -> List[Finding]:
    """Check for SQL injection vulnerabilities"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential SQL injection vulnerability detected', confidence=0.8, evidence={'vulnerability_type': 'sql_injection', 'pattern_matched': pattern, 'line_content': line.strip()}))
    return findings

def _check_xss_vulnerabilities(self, content: str, file_path: Path) -> List[Finding]:
    """Check for XSS vulnerabilities"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern in self.xss_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential XSS vulnerability detected', confidence=0.7, evidence={'vulnerability_type': 'xss', 'pattern_matched': pattern, 'line_content': line.strip()}))
    return findings

def _check_command_injection(self, content: str, file_path: Path) -> List[Finding]:
    """Check for command injection vulnerabilities"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern in self.command_injection_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.CRITICAL, location=CodeLocation(str(file_path), line_num), description='Potential command injection vulnerability detected', confidence=0.8, evidence={'vulnerability_type': 'command_injection', 'pattern_matched': pattern, 'line_content': line.strip()}))
    return findings

def _check_hardcoded_secrets(self, content: str, file_path: Path) -> List[Finding]:
    """Check for hardcoded secrets and credentials"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern, secret_type in self.secret_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description=f"Hardcoded {secret_type.replace('_', ' ')} detected", confidence=0.9, evidence={'vulnerability_type': 'hardcoded_secret', 'secret_type': secret_type, 'line_content': line.strip()}))
    return findings

def _check_crypto_issues(self, content: str, file_path: Path) -> List[Finding]:
    """Check for cryptographic issues"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern, crypto_issue in self.crypto_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), line_num), description=f"Insecure cryptographic practice: {crypto_issue.replace('_', ' ')}", confidence=0.8, evidence={'vulnerability_type': 'crypto_issue', 'issue_type': crypto_issue, 'line_content': line.strip()}))
    return findings

def _check_path_traversal(self, content: str, file_path: Path) -> List[Finding]:
    """Check for path traversal vulnerabilities"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, line):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential path traversal vulnerability detected', confidence=0.7, evidence={'vulnerability_type': 'path_traversal', 'pattern_matched': pattern, 'line_content': line.strip()}))
    return findings

def _check_file_permissions(self, file_path: Path) -> List[Finding]:
    """Check file permissions for security issues"""
    findings = []
    try:
        import stat
from src.rm_ddd.core.health import ModuleHealth

        file_stat = file_path.stat()
        if file_stat.st_mode & stat.S_IWOTH:
            findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), 1), description='File is world-writable (security risk)', confidence=0.9, evidence={'vulnerability_type': 'file_permissions', 'permissions': oct(file_stat.st_mode)[-3:]}))
        if file_path.suffix.lower() in ['.sh', '.bat', '.cmd', '.exe'] and file_stat.st_mode & stat.S_IXUSR:
            findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.LOW, location=CodeLocation(str(file_path), 1), description='Executable file detected - verify necessity', confidence=0.6, evidence={'vulnerability_type': 'executable_file', 'file_extension': file_path.suffix}))
    except Exception as e:
        logger.debug(f'Could not check permissions for {file_path}: {str(e)}')
    return findings

def _check_python_security(self, content: str, file_path: Path) -> List[Finding]:
    """Python-specific security checks"""
    findings = []
    lines = content.splitlines()
    python_patterns = [('pickle\\.loads?\\s*\\(', 'unsafe_deserialization', Severity.HIGH), ('yaml\\.load\\s*\\(', 'unsafe_yaml_load', Severity.HIGH), ('input\\s*\\(\\s*\\)', 'unsafe_input', Severity.MEDIUM), ('__import__\\s*\\(', 'dynamic_import', Severity.MEDIUM)]
    for line_num, line in enumerate(lines, 1):
        for pattern, issue_type, severity in python_patterns:
            if re.search(pattern, line):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"Python security issue: {issue_type.replace('_', ' ')}", confidence=0.8, evidence={'vulnerability_type': issue_type, 'language': 'python', 'line_content': line.strip()}))
    return findings

def _check_javascript_security(self, content: str, file_path: Path) -> List[Finding]:
    """JavaScript-specific security checks"""
    findings = []
    lines = content.splitlines()
    js_patterns = [('localStorage\\.setItem\\s*\\(\\s*["\\\'][^"\\\']*password', 'password_in_localstorage', Severity.HIGH), ('sessionStorage\\.setItem\\s*\\(\\s*["\\\'][^"\\\']*password', 'password_in_sessionstorage', Severity.HIGH), ('window\\.location\\.href\\s*=.*\\+', 'open_redirect', Severity.MEDIUM), ('postMessage\\s*\\(\\s*.*\\*', 'unsafe_postmessage', Severity.MEDIUM)]
    for line_num, line in enumerate(lines, 1):
        for pattern, issue_type, severity in js_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"JavaScript security issue: {issue_type.replace('_', ' ')}", confidence=0.7, evidence={'vulnerability_type': issue_type, 'language': 'javascript', 'line_content': line.strip()}))
    return findings

def _check_java_security(self, content: str, file_path: Path) -> List[Finding]:
    """Java-specific security checks"""
    findings = []
    lines = content.splitlines()
    java_patterns = [('Runtime\\.getRuntime\\(\\)\\.exec', 'runtime_exec', Severity.HIGH), ('ObjectInputStream\\s*\\(', 'unsafe_deserialization', Severity.HIGH), ('Random\\s*\\(\\s*\\)', 'weak_random', Severity.MEDIUM), ('MessageDigest\\.getInstance\\s*\\(\\s*["\\\']MD5', 'weak_hash', Severity.MEDIUM)]
    for line_num, line in enumerate(lines, 1):
        for pattern, issue_type, severity in java_patterns:
            if re.search(pattern, line):
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"Java security issue: {issue_type.replace('_', ' ')}", confidence=0.8, evidence={'vulnerability_type': issue_type, 'language': 'java', 'line_content': line.strip()}))
    return findings

def _get_checks_performed(self) -> List[str]:
    """Get list of security checks performed"""
    return ['sql_injection', 'xss_vulnerabilities', 'command_injection', 'hardcoded_secrets', 'crypto_issues', 'path_traversal', 'file_permissions', 'language_specific_checks']

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

