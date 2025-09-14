"""
Rm Validator Core Validation

This module was extracted from rm_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import inspect
import importlib.util
import os
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity, RMComplianceStatus
from ...core.reflective_module import ReflectiveModule

def validate_rm_interface_implementation(self, module_path: str) -> RMInterfaceResult:
    """
        Validate that a module properly implements the RM interface.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            RMInterfaceResult with validation details
        """
    issues = []
    missing_methods = []
    invalid_methods = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code)
        rm_classes = self._find_rm_classes(tree, source_code)
        if not rm_classes:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description='No ReflectiveModule classes found in module', affected_files=[module_path], remediation_steps=['Create a class that inherits from ReflectiveModule', 'Implement all required RM interface methods'], blocking_merge=True))
            return RMInterfaceResult(module_path=module_path, implements_rm_interface=False, missing_methods=list(self.REQUIRED_RM_METHODS.keys()), invalid_methods=[], interface_compliance_score=0.0, issues=issues)
        for class_node in rm_classes:
            class_missing, class_invalid = self._validate_class_methods(class_node, module_path)
            missing_methods.extend(class_missing)
            invalid_methods.extend(class_invalid)
        for method_name in missing_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.CRITICAL, description=f'Missing required RM method: {method_name}', affected_files=[module_path], remediation_steps=[f'Implement the {method_name} method', f"Method should: {self.REQUIRED_RM_METHODS.get(method_name, 'Follow RM interface specification')}"], blocking_merge=True))
        for method_name in invalid_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Invalid RM method implementation: {method_name}', affected_files=[module_path], remediation_steps=[f'Fix the {method_name} method implementation', f'Ensure method signature and behavior match RM specification'], blocking_merge=False))
        total_required = len(self.REQUIRED_RM_METHODS)
        implemented_required = total_required - len(missing_methods)
        interface_compliance_score = implemented_required / total_required if total_required > 0 else 0.0
        implements_rm_interface = len(missing_methods) == 0 and len(rm_classes) > 0
        return RMInterfaceResult(module_path=module_path, implements_rm_interface=implements_rm_interface, missing_methods=missing_methods, invalid_methods=invalid_methods, interface_compliance_score=interface_compliance_score, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to validate RM interface: {str(e)}', affected_files=[module_path], remediation_steps=['Fix syntax errors in the module', 'Ensure module is valid Python code'], blocking_merge=True))
        return RMInterfaceResult(module_path=module_path, implements_rm_interface=False, missing_methods=list(self.REQUIRED_RM_METHODS.keys()), invalid_methods=[], interface_compliance_score=0.0, issues=issues)

def check_size_constraints(self, module_path: str) -> SizeConstraintResult:
    """
        Check that module meets size constraints (≤200 lines) and single responsibility.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            SizeConstraintResult with validation details
        """
    issues = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        code_lines = [line.strip() for line in lines if line.strip() and (not line.strip().startswith('#'))]
        line_count = len(code_lines)
        meets_size_constraint = line_count <= self.max_lines_per_module
        if not meets_size_constraint:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Module exceeds size constraint: {line_count} lines (max: {self.max_lines_per_module})', affected_files=[module_path], remediation_steps=['Refactor module to reduce size', 'Split large classes into smaller, focused components', 'Extract utility functions to separate modules', 'Consider breaking module into multiple focused modules'], blocking_merge=True))
        complexity_indicators = self._analyze_complexity(module_path)
        single_responsibility_score = self._calculate_single_responsibility_score(complexity_indicators)
        if single_responsibility_score < 0.7:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Low single responsibility score: {single_responsibility_score:.2f}', affected_files=[module_path], remediation_steps=['Reduce module complexity', 'Ensure module has a single, clear responsibility', 'Extract unrelated functionality to separate modules'], blocking_merge=False))
        self._check_architectural_patterns(module_path, complexity_indicators, issues)
        return SizeConstraintResult(module_path=module_path, line_count=line_count, meets_size_constraint=meets_size_constraint, single_responsibility_score=single_responsibility_score, complexity_indicators=complexity_indicators, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Failed to check size constraints: {str(e)}', affected_files=[module_path], remediation_steps=['Fix file access issues', 'Ensure module file is readable'], blocking_merge=True))
        return SizeConstraintResult(module_path=module_path, line_count=0, meets_size_constraint=False, single_responsibility_score=0.0, complexity_indicators={}, issues=issues)

def validate_health_monitoring(self, module_path: str) -> HealthMonitoringResult:
    """
        Validate health monitoring implementation in RM components.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            HealthMonitoringResult with validation details
        """
    issues = []
    health_methods_implemented = []
    missing_health_methods = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code)
        method_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_names.add(node.name)
        for method_name, description in self.HEALTH_MONITORING_METHODS.items():
            if method_name in method_names:
                health_methods_implemented.append(method_name)
            else:
                missing_health_methods.append(method_name)
                if method_name in ['is_healthy', 'get_health_indicators']:
                    issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.CRITICAL, description=f'Missing health monitoring method: {method_name}', affected_files=[module_path], remediation_steps=[f'Implement the {method_name} method', f'Method should: {description}'], blocking_merge=True))
        has_health_indicators = 'self._health_indicators' in source_code
        has_critical_health_methods = 'is_healthy' in method_names and 'get_health_indicators' in method_names
        if not has_health_indicators and has_critical_health_methods:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.MEDIUM, description='No health indicators found in module', affected_files=[module_path], remediation_steps=['Add health indicators to track module status', 'Use _update_health_indicator method to maintain health state'], blocking_merge=False))
        total_health_methods = len(self.HEALTH_MONITORING_METHODS)
        implemented_health_methods = len(health_methods_implemented)
        health_monitoring_score = implemented_health_methods / total_health_methods if total_health_methods > 0 else 0.0
        has_health_monitoring = len(missing_health_methods) == 0
        return HealthMonitoringResult(module_path=module_path, has_health_monitoring=has_health_monitoring, health_methods_implemented=health_methods_implemented, missing_health_methods=missing_health_methods, health_monitoring_score=health_monitoring_score, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to validate health monitoring: {str(e)}', affected_files=[module_path], remediation_steps=['Fix syntax errors in the module', 'Ensure module is valid Python code'], blocking_merge=True))
        return HealthMonitoringResult(module_path=module_path, has_health_monitoring=False, health_methods_implemented=[], missing_health_methods=list(self.HEALTH_MONITORING_METHODS.keys()), health_monitoring_score=0.0, issues=issues)

def check_registry_integration(self, module_path: str) -> RegistryIntegrationResult:
    """
        Check proper registry integration for RM components.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            RegistryIntegrationResult with validation details
        """
    issues = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        has_registration_method = 'register_rm_documentation' in source_code
        has_registry_imports = any((pattern in source_code for pattern in ['DocumentManagementRM', 'from beast_mode.documentation', 'import.*registry']))
        properly_registered = has_registration_method and has_registry_imports
        if not has_registration_method:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.MEDIUM, description='No registry registration method found', affected_files=[module_path], remediation_steps=['Implement register_rm_documentation method', 'Call registration method during module initialization'], blocking_merge=False))
        if not has_registry_imports:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.LOW, description='No registry-related imports found', affected_files=[module_path], remediation_steps=['Import necessary registry components', 'Add DocumentManagementRM import if using documentation registry'], blocking_merge=False))
        registry_compliance_score = 1.0
        if not has_registration_method:
            registry_compliance_score -= 0.6
        if not has_registry_imports:
            registry_compliance_score -= 0.4
        registry_compliance_score = max(0.0, registry_compliance_score)
        return RegistryIntegrationResult(module_path=module_path, properly_registered=properly_registered, registration_method_present=has_registration_method, registry_compliance_score=registry_compliance_score, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.RM_NON_COMPLIANCE, severity=IssueSeverity.HIGH, description=f'Failed to check registry integration: {str(e)}', affected_files=[module_path], remediation_steps=['Fix file access issues', 'Ensure module file is readable'], blocking_merge=True))
        return RegistryIntegrationResult(module_path=module_path, properly_registered=False, registration_method_present=False, registry_compliance_score=0.0, issues=issues)

def validate_rm_compliance(self, module_path: str) -> RMComplianceStatus:
    """
        Perform comprehensive RM compliance validation.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            RMComplianceStatus with overall compliance assessment
        """
    interface_result = self.validate_rm_interface_implementation(module_path)
    size_result = self.check_size_constraints(module_path)
    health_result = self.validate_health_monitoring(module_path)
    registry_result = self.check_registry_integration(module_path)
    all_issues = []
    all_issues.extend(interface_result.issues)
    all_issues.extend(size_result.issues)
    all_issues.extend(health_result.issues)
    all_issues.extend(registry_result.issues)
    scores = [interface_result.interface_compliance_score, 1.0 if size_result.meets_size_constraint else 0.0, health_result.health_monitoring_score, registry_result.registry_compliance_score]
    overall_score = sum(scores) / len(scores) if scores else 0.0
    return RMComplianceStatus(interface_implemented=interface_result.implements_rm_interface, size_constraints_met=size_result.meets_size_constraint, health_monitoring_present=health_result.has_health_monitoring, registry_integrated=registry_result.properly_registered, compliance_score=overall_score, issues=all_issues)

def _validate_class_methods(self, class_node: ast.ClassDef, module_path: str) -> tuple[List[str], List[str]]:
    """Validate methods in a ReflectiveModule class."""
    missing_methods = []
    invalid_methods = []
    class_methods = set()
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            class_methods.add(node.name)
    for method_name in self.REQUIRED_RM_METHODS:
        if method_name not in class_methods:
            missing_methods.append(method_name)
    return (missing_methods, invalid_methods)

def _check_architectural_patterns(self, module_path: str, complexity_indicators: Dict[str, Any], issues: List[ComplianceIssue]) -> None:
    """Check for specific architectural patterns and violations."""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        class_count = complexity_indicators.get('class_count', 0)
        if class_count > 5:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Too many classes in module: {class_count} (recommended: ≤5)', affected_files=[module_path], remediation_steps=['Split module into multiple focused modules', 'Group related classes into separate modules', 'Consider using composition over multiple classes'], blocking_merge=False))
        import_count = complexity_indicators.get('import_count', 0)
        if import_count > 20:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Too many imports: {import_count} (recommended: ≤20)', affected_files=[module_path], remediation_steps=['Reduce dependencies by removing unused imports', 'Consider dependency injection to reduce coupling', 'Split module to reduce external dependencies'], blocking_merge=False))
        max_nesting = complexity_indicators.get('max_nesting_depth', 0)
        if max_nesting > 4:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Deep nesting detected: {max_nesting} levels (recommended: ≤4)', affected_files=[module_path], remediation_steps=['Refactor nested conditions using early returns', 'Extract complex logic into separate methods', 'Use guard clauses to reduce nesting'], blocking_merge=False))
        function_count = complexity_indicators.get('function_count', 0)
        if function_count > 25:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Too many methods: {function_count} (recommended: ≤25)', affected_files=[module_path], remediation_steps=['Split large classes into smaller, focused classes', 'Extract utility methods to separate modules', 'Apply single responsibility principle more strictly'], blocking_merge=False))
        if '"""' not in source_code and "'''" not in source_code:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.LOW, description='No module-level docstring found', affected_files=[module_path], remediation_steps=['Add module-level docstring describing purpose', 'Document all public classes and methods', 'Follow PEP 257 docstring conventions'], blocking_merge=False))
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.LOW, description=f'Could not perform architectural pattern analysis: {str(e)}', affected_files=[module_path], remediation_steps=['Ensure module is syntactically valid', 'Check file permissions and accessibility'], blocking_merge=False))
