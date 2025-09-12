"""
RM (Reflective Module) architectural compliance validator.

Validates that components follow RM interface requirements and architectural constraints
as defined in the Beast Mode Framework standards.
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


@dataclass
class RMInterfaceResult:
    """Results of RM interface validation."""
    module_path: str
    implements_rm_interface: bool
    missing_methods: List[str]
    invalid_methods: List[str]
    interface_compliance_score: float
    issues: List[ComplianceIssue]


@dataclass
class SizeConstraintResult:
    """Results of module size constraint validation."""
    module_path: str
    line_count: int
    meets_size_constraint: bool  # ≤200 lines
    single_responsibility_score: float
    complexity_indicators: Dict[str, Any]
    issues: List[ComplianceIssue]


@dataclass
class HealthMonitoringResult:
    """Results of health monitoring validation."""
    module_path: str
    has_health_monitoring: bool
    health_methods_implemented: List[str]
    missing_health_methods: List[str]
    health_monitoring_score: float
    issues: List[ComplianceIssue]


@dataclass
class RegistryIntegrationResult:
    """Results of registry integration validation."""
    module_path: str
    properly_registered: bool
    registration_method_present: bool
    registry_compliance_score: float
    issues: List[ComplianceIssue]


class RMValidator:
    """
    RM architectural compliance validator.
    
    Validates that components follow RM interface requirements:
    - Implements required ReflectiveModule methods
    - Meets size constraints (≤200 lines)
    - Implements health monitoring
    - Properly integrates with registry
    """
    
    # Required RM interface methods
    REQUIRED_RM_METHODS = {
        'get_module_status': 'Must return Dict[str, Any] with module operational status',
        'is_healthy': 'Must return bool indicating module health',
        'get_health_indicators': 'Must return Dict[str, Any] with detailed health metrics',
        '_get_primary_responsibility': 'Must return str defining single primary responsibility'
    }
    
    # Optional but recommended RM methods
    RECOMMENDED_RM_METHODS = {
        'degrade_gracefully': 'Should handle graceful degradation',
        'maintain_single_responsibility': 'Should validate single responsibility',
        'get_documentation_compliance_status': 'Should check documentation compliance',
        'register_rm_documentation': 'Should register documentation'
    }
    
    # Health monitoring related methods
    HEALTH_MONITORING_METHODS = {
        'is_healthy': 'Core health check method',
        'get_health_indicators': 'Detailed health metrics',
        '_update_health_indicator': 'Internal health indicator updates'
    }
    
    def __init__(self):
        self.max_lines_per_module = 200
        
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
            # Parse the module AST
            with open(module_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            # Find class definitions that should inherit from ReflectiveModule
            rm_classes = self._find_rm_classes(tree, source_code)
            
            if not rm_classes:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.HIGH,
                    description="No ReflectiveModule classes found in module",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Create a class that inherits from ReflectiveModule",
                        "Implement all required RM interface methods"
                    ],
                    blocking_merge=True
                ))
                
                return RMInterfaceResult(
                    module_path=module_path,
                    implements_rm_interface=False,
                    missing_methods=list(self.REQUIRED_RM_METHODS.keys()),
                    invalid_methods=[],
                    interface_compliance_score=0.0,
                    issues=issues
                )
            
            # Validate each RM class
            for class_node in rm_classes:
                class_missing, class_invalid = self._validate_class_methods(
                    class_node, module_path
                )
                missing_methods.extend(class_missing)
                invalid_methods.extend(class_invalid)
            
            # Create issues for missing methods
            for method_name in missing_methods:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Missing required RM method: {method_name}",
                    affected_files=[module_path],
                    remediation_steps=[
                        f"Implement the {method_name} method",
                        f"Method should: {self.REQUIRED_RM_METHODS.get(method_name, 'Follow RM interface specification')}"
                    ],
                    blocking_merge=True
                ))
            
            # Create issues for invalid methods
            for method_name in invalid_methods:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.HIGH,
                    description=f"Invalid RM method implementation: {method_name}",
                    affected_files=[module_path],
                    remediation_steps=[
                        f"Fix the {method_name} method implementation",
                        f"Ensure method signature and behavior match RM specification"
                    ],
                    blocking_merge=False
                ))
            
            # Calculate compliance score
            total_required = len(self.REQUIRED_RM_METHODS)
            implemented_required = total_required - len(missing_methods)
            interface_compliance_score = implemented_required / total_required if total_required > 0 else 0.0
            
            implements_rm_interface = len(missing_methods) == 0 and len(rm_classes) > 0
            
            return RMInterfaceResult(
                module_path=module_path,
                implements_rm_interface=implements_rm_interface,
                missing_methods=missing_methods,
                invalid_methods=invalid_methods,
                interface_compliance_score=interface_compliance_score,
                issues=issues
            )
            
        except Exception as e:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.HIGH,
                description=f"Failed to validate RM interface: {str(e)}",
                affected_files=[module_path],
                remediation_steps=[
                    "Fix syntax errors in the module",
                    "Ensure module is valid Python code"
                ],
                blocking_merge=True
            ))
            
            return RMInterfaceResult(
                module_path=module_path,
                implements_rm_interface=False,
                missing_methods=list(self.REQUIRED_RM_METHODS.keys()),
                invalid_methods=[],
                interface_compliance_score=0.0,
                issues=issues
            )
    
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
            
            # Count non-empty, non-comment lines
            code_lines = [
                line.strip() for line in lines 
                if line.strip() and not line.strip().startswith('#')
            ]
            line_count = len(code_lines)
            
            # Check size constraint
            meets_size_constraint = line_count <= self.max_lines_per_module
            
            if not meets_size_constraint:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.HIGH,
                    description=f"Module exceeds size constraint: {line_count} lines (max: {self.max_lines_per_module})",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Refactor module to reduce size",
                        "Split large classes into smaller, focused components",
                        "Extract utility functions to separate modules",
                        "Consider breaking module into multiple focused modules"
                    ],
                    blocking_merge=True
                ))
            
            # Analyze complexity indicators
            complexity_indicators = self._analyze_complexity(module_path)
            
            # Calculate single responsibility score based on complexity
            single_responsibility_score = self._calculate_single_responsibility_score(
                complexity_indicators
            )
            
            if single_responsibility_score < 0.7:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.MEDIUM,
                    description=f"Low single responsibility score: {single_responsibility_score:.2f}",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Reduce module complexity",
                        "Ensure module has a single, clear responsibility",
                        "Extract unrelated functionality to separate modules"
                    ],
                    blocking_merge=False
                ))
            
            # Additional architectural pattern checks
            self._check_architectural_patterns(module_path, complexity_indicators, issues)
            
            return SizeConstraintResult(
                module_path=module_path,
                line_count=line_count,
                meets_size_constraint=meets_size_constraint,
                single_responsibility_score=single_responsibility_score,
                complexity_indicators=complexity_indicators,
                issues=issues
            )
            
        except Exception as e:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                severity=IssueSeverity.HIGH,
                description=f"Failed to check size constraints: {str(e)}",
                affected_files=[module_path],
                remediation_steps=[
                    "Fix file access issues",
                    "Ensure module file is readable"
                ],
                blocking_merge=True
            ))
            
            return SizeConstraintResult(
                module_path=module_path,
                line_count=0,
                meets_size_constraint=False,
                single_responsibility_score=0.0,
                complexity_indicators={},
                issues=issues
            )
    
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
            
            # Find all method definitions
            method_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_names.add(node.name)
            
            # Check for health monitoring methods
            for method_name, description in self.HEALTH_MONITORING_METHODS.items():
                if method_name in method_names:
                    health_methods_implemented.append(method_name)
                else:
                    missing_health_methods.append(method_name)
                    
                    # Only create issues for critical health methods
                    if method_name in ['is_healthy', 'get_health_indicators']:
                        issues.append(ComplianceIssue(
                            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                            severity=IssueSeverity.CRITICAL,
                            description=f"Missing health monitoring method: {method_name}",
                            affected_files=[module_path],
                            remediation_steps=[
                                f"Implement the {method_name} method",
                                f"Method should: {description}"
                            ],
                            blocking_merge=True
                        ))
            
            # Check for health indicator usage (more specific search)
            has_health_indicators = 'self._health_indicators' in source_code
            has_critical_health_methods = 'is_healthy' in method_names and 'get_health_indicators' in method_names
            
            if not has_health_indicators and has_critical_health_methods:
                # Flag missing indicators if critical health methods are implemented but no indicators used
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.MEDIUM,
                    description="No health indicators found in module",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Add health indicators to track module status",
                        "Use _update_health_indicator method to maintain health state"
                    ],
                    blocking_merge=False
                ))
            
            # Calculate health monitoring score
            total_health_methods = len(self.HEALTH_MONITORING_METHODS)
            implemented_health_methods = len(health_methods_implemented)
            health_monitoring_score = implemented_health_methods / total_health_methods if total_health_methods > 0 else 0.0
            
            has_health_monitoring = len(missing_health_methods) == 0
            
            return HealthMonitoringResult(
                module_path=module_path,
                has_health_monitoring=has_health_monitoring,
                health_methods_implemented=health_methods_implemented,
                missing_health_methods=missing_health_methods,
                health_monitoring_score=health_monitoring_score,
                issues=issues
            )
            
        except Exception as e:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.HIGH,
                description=f"Failed to validate health monitoring: {str(e)}",
                affected_files=[module_path],
                remediation_steps=[
                    "Fix syntax errors in the module",
                    "Ensure module is valid Python code"
                ],
                blocking_merge=True
            ))
            
            return HealthMonitoringResult(
                module_path=module_path,
                has_health_monitoring=False,
                health_methods_implemented=[],
                missing_health_methods=list(self.HEALTH_MONITORING_METHODS.keys()),
                health_monitoring_score=0.0,
                issues=issues
            )
    
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
            
            # Check for registry-related patterns
            has_registration_method = 'register_rm_documentation' in source_code
            has_registry_imports = any(
                pattern in source_code for pattern in [
                    'DocumentManagementRM',
                    'from beast_mode.documentation',
                    'import.*registry'
                ]
            )
            
            properly_registered = has_registration_method and has_registry_imports
            
            if not has_registration_method:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.MEDIUM,
                    description="No registry registration method found",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Implement register_rm_documentation method",
                        "Call registration method during module initialization"
                    ],
                    blocking_merge=False
                ))
            
            if not has_registry_imports:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                    severity=IssueSeverity.LOW,
                    description="No registry-related imports found",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Import necessary registry components",
                        "Add DocumentManagementRM import if using documentation registry"
                    ],
                    blocking_merge=False
                ))
            
            # Calculate registry compliance score
            registry_compliance_score = 1.0
            if not has_registration_method:
                registry_compliance_score -= 0.6
            if not has_registry_imports:
                registry_compliance_score -= 0.4
            registry_compliance_score = max(0.0, registry_compliance_score)
            
            return RegistryIntegrationResult(
                module_path=module_path,
                properly_registered=properly_registered,
                registration_method_present=has_registration_method,
                registry_compliance_score=registry_compliance_score,
                issues=issues
            )
            
        except Exception as e:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.HIGH,
                description=f"Failed to check registry integration: {str(e)}",
                affected_files=[module_path],
                remediation_steps=[
                    "Fix file access issues",
                    "Ensure module file is readable"
                ],
                blocking_merge=True
            ))
            
            return RegistryIntegrationResult(
                module_path=module_path,
                properly_registered=False,
                registration_method_present=False,
                registry_compliance_score=0.0,
                issues=issues
            )
    
    def validate_rm_compliance(self, module_path: str) -> RMComplianceStatus:
        """
        Perform comprehensive RM compliance validation.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            RMComplianceStatus with overall compliance assessment
        """
        # Run all validation checks
        interface_result = self.validate_rm_interface_implementation(module_path)
        size_result = self.check_size_constraints(module_path)
        health_result = self.validate_health_monitoring(module_path)
        registry_result = self.check_registry_integration(module_path)
        
        # Collect all issues
        all_issues = []
        all_issues.extend(interface_result.issues)
        all_issues.extend(size_result.issues)
        all_issues.extend(health_result.issues)
        all_issues.extend(registry_result.issues)
        
        # Calculate overall compliance score
        scores = [
            interface_result.interface_compliance_score,
            1.0 if size_result.meets_size_constraint else 0.0,
            health_result.health_monitoring_score,
            registry_result.registry_compliance_score
        ]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return RMComplianceStatus(
            interface_implemented=interface_result.implements_rm_interface,
            size_constraints_met=size_result.meets_size_constraint,
            health_monitoring_present=health_result.has_health_monitoring,
            registry_integrated=registry_result.properly_registered,
            compliance_score=overall_score,
            issues=all_issues
        )
    
    def _find_rm_classes(self, tree: ast.AST, source_code: str) -> List[ast.ClassDef]:
        """Find classes that inherit from ReflectiveModule."""
        rm_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from ReflectiveModule
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'ReflectiveModule':
                        rm_classes.append(node)
                    elif isinstance(base, ast.Attribute):
                        # Handle cases like module.ReflectiveModule
                        if base.attr == 'ReflectiveModule':
                            rm_classes.append(node)
        
        return rm_classes
    
    def _validate_class_methods(self, class_node: ast.ClassDef, module_path: str) -> tuple[List[str], List[str]]:
        """Validate methods in a ReflectiveModule class."""
        missing_methods = []
        invalid_methods = []
        
        # Get all method names in the class
        class_methods = set()
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                class_methods.add(node.name)
        
        # Check for required methods
        for method_name in self.REQUIRED_RM_METHODS:
            if method_name not in class_methods:
                missing_methods.append(method_name)
        
        return missing_methods, invalid_methods
    
    def _analyze_complexity(self, module_path: str) -> Dict[str, Any]:
        """Analyze module complexity indicators."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            # Count various complexity indicators
            class_count = 0
            function_count = 0
            import_count = 0
            max_nesting_depth = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_count += 1
                elif isinstance(node, ast.FunctionDef):
                    function_count += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_count += 1
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                    # Simple nesting depth calculation
                    depth = self._calculate_nesting_depth(node)
                    max_nesting_depth = max(max_nesting_depth, depth)
            
            return {
                'class_count': class_count,
                'function_count': function_count,
                'import_count': import_count,
                'max_nesting_depth': max_nesting_depth,
                'complexity_score': self._calculate_complexity_score(
                    class_count, function_count, import_count, max_nesting_depth
                )
            }
            
        except Exception:
            return {
                'class_count': 0,
                'function_count': 0,
                'import_count': 0,
                'max_nesting_depth': 0,
                'complexity_score': 1.0  # Default to high complexity on error
            }
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 1) -> int:
        """Calculate maximum nesting depth for a node."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _calculate_complexity_score(self, class_count: int, function_count: int, 
                                  import_count: int, max_nesting_depth: int) -> float:
        """Calculate complexity score (lower is better)."""
        # Normalize each factor
        class_factor = min(class_count / 5.0, 1.0)  # Penalize > 5 classes
        function_factor = min(function_count / 20.0, 1.0)  # Penalize > 20 functions
        import_factor = min(import_count / 15.0, 1.0)  # Penalize > 15 imports
        nesting_factor = min(max_nesting_depth / 5.0, 1.0)  # Penalize > 5 levels
        
        # Weighted average (higher weight on classes and nesting)
        complexity = (
            class_factor * 0.3 +
            function_factor * 0.2 +
            import_factor * 0.2 +
            nesting_factor * 0.3
        )
        
        return complexity
    
    def _calculate_single_responsibility_score(self, complexity_indicators: Dict[str, Any]) -> float:
        """Calculate single responsibility score based on complexity."""
        complexity_score = complexity_indicators.get('complexity_score', 1.0)
        
        # Invert complexity score (lower complexity = higher responsibility score)
        responsibility_score = 1.0 - complexity_score
        
        # Additional penalties for specific indicators
        class_count = complexity_indicators.get('class_count', 0)
        if class_count > 3:  # More than 3 classes suggests multiple responsibilities
            responsibility_score *= 0.8
        
        function_count = complexity_indicators.get('function_count', 0)
        if function_count > 15:  # Too many functions suggests multiple responsibilities
            responsibility_score *= 0.9
        
        # Additional architectural checks
        import_count = complexity_indicators.get('import_count', 0)
        if import_count > 20:  # Too many imports suggests coupling to many modules
            responsibility_score *= 0.85
        
        max_nesting_depth = complexity_indicators.get('max_nesting_depth', 0)
        if max_nesting_depth > 4:  # Deep nesting suggests complex logic
            responsibility_score *= 0.9
        
        return max(0.0, min(1.0, responsibility_score))
    
    def _check_architectural_patterns(self, module_path: str, complexity_indicators: Dict[str, Any], issues: List[ComplianceIssue]) -> None:
        """Check for specific architectural patterns and violations."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Check for excessive class coupling
            class_count = complexity_indicators.get('class_count', 0)
            if class_count > 5:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.HIGH,
                    description=f"Too many classes in module: {class_count} (recommended: ≤5)",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Split module into multiple focused modules",
                        "Group related classes into separate modules",
                        "Consider using composition over multiple classes"
                    ],
                    blocking_merge=False
                ))
            
            # Check for excessive imports (high coupling)
            import_count = complexity_indicators.get('import_count', 0)
            if import_count > 20:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.MEDIUM,
                    description=f"Too many imports: {import_count} (recommended: ≤20)",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Reduce dependencies by removing unused imports",
                        "Consider dependency injection to reduce coupling",
                        "Split module to reduce external dependencies"
                    ],
                    blocking_merge=False
                ))
            
            # Check for deep nesting (complex control flow)
            max_nesting = complexity_indicators.get('max_nesting_depth', 0)
            if max_nesting > 4:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.MEDIUM,
                    description=f"Deep nesting detected: {max_nesting} levels (recommended: ≤4)",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Refactor nested conditions using early returns",
                        "Extract complex logic into separate methods",
                        "Use guard clauses to reduce nesting"
                    ],
                    blocking_merge=False
                ))
            
            # Check for potential god class pattern
            function_count = complexity_indicators.get('function_count', 0)
            if function_count > 25:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.HIGH,
                    description=f"Too many methods: {function_count} (recommended: ≤25)",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Split large classes into smaller, focused classes",
                        "Extract utility methods to separate modules",
                        "Apply single responsibility principle more strictly"
                    ],
                    blocking_merge=False
                ))
            
            # Check for missing docstrings (documentation compliance)
            if '"""' not in source_code and "'''" not in source_code:
                issues.append(ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.LOW,
                    description="No module-level docstring found",
                    affected_files=[module_path],
                    remediation_steps=[
                        "Add module-level docstring describing purpose",
                        "Document all public classes and methods",
                        "Follow PEP 257 docstring conventions"
                    ],
                    blocking_merge=False
                ))
            
        except Exception as e:
            # Don't fail the entire validation if architectural pattern checking fails
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                severity=IssueSeverity.LOW,
                description=f"Could not perform architectural pattern analysis: {str(e)}",
                affected_files=[module_path],
                remediation_steps=[
                    "Ensure module is syntactically valid",
                    "Check file permissions and accessibility"
                ],
                blocking_merge=False
            ))