"""
Domain Validation and Consistency Checking System

This module provides comprehensive validation for domain structures,
dependency consistency, and cross-domain relationship validation.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .base import DomainSystemComponent
from .models import (
    Domain, DomainCollection, ValidationResult, HealthIssue, 
    IssueSeverity, IssueCategory, DependencyGraph
)
from .exceptions import DomainValidationError


@dataclass
class ValidationRule:
    """Individual validation rule"""
    name: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    validator_func: callable
    
    def validate(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
        """Execute validation rule"""
        try:
            return self.validator_func(domain, context) or []
        except Exception as e:
            return [HealthIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.VALIDATION,
                description=f"Validation rule '{self.name}' failed: {str(e)}",
                suggested_fix="Check validation rule implementation"
            )]


@dataclass
class ConsistencyCheck:
    """Cross-domain consistency check"""
    name: str
    description: str
    severity: IssueSeverity
    checker_func: callable
    
    def check(self, domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        """Execute consistency check"""
        try:
            return self.checker_func(domains, context) or []
        except Exception as e:
            return [HealthIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.VALIDATION,
                description=f"Consistency check '{self.name}' failed: {str(e)}",
                suggested_fix="Check consistency check implementation"
            )]


class DomainValidator(DomainSystemComponent):
    """
    Comprehensive domain validation and consistency checking system
    
    Features:
    - Schema validation against domain structure
    - Dependency validation and circular dependency detection
    - File pattern validation
    - Cross-domain consistency checking
    - Custom validation rules
    - Detailed error reporting with suggestions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_validator", config)
        
        # Validation configuration
        self.strict_mode = self.config.get('strict_validation', False)
        self.check_filesystem = self.config.get('check_filesystem', True)
        self.max_dependency_depth = self.config.get('max_dependency_depth', 10)
        self.required_fields = self.config.get('required_fields', [
            'name', 'description', 'patterns', 'tools'
        ])
        
        # Validation rules and consistency checks
        self._validation_rules: List[ValidationRule] = []
        self._consistency_checks: List[ConsistencyCheck] = []
        
        # Statistics
        self.validations_performed = 0
        self.consistency_checks_performed = 0
        self.issues_found = 0
        
        # Initialize built-in rules
        self._initialize_builtin_rules()
        self._initialize_builtin_consistency_checks()
        
        self.logger.info("Initialized DomainValidator with built-in rules")
    
    def validate_domain(self, domain: Domain, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate a single domain against all rules"""
        with self._time_operation("validate_domain"):
            self.validations_performed += 1
            
            context = context or {}
            context['validator'] = self
            
            all_issues = []
            
            # Run all validation rules
            for rule in self._validation_rules:
                try:
                    issues = rule.validate(domain, context)
                    all_issues.extend(issues)
                except Exception as e:
                    self.logger.error(f"Validation rule '{rule.name}' failed: {e}")
                    all_issues.append(HealthIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.VALIDATION,
                        description=f"Validation rule error: {str(e)}",
                        suggested_fix="Check validation rule implementation"
                    ))
            
            # Categorize issues
            errors = [issue for issue in all_issues if issue.severity == IssueSeverity.CRITICAL]
            warnings = [issue for issue in all_issues if issue.severity == IssueSeverity.WARNING]
            suggestions = [issue.suggested_fix for issue in all_issues if issue.severity == IssueSeverity.INFO]
            
            self.issues_found += len(all_issues)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=[issue.description for issue in errors],
                warnings=[issue.description for issue in warnings],
                suggestions=suggestions
            )
    
    def validate_domain_collection(self, domains: DomainCollection) -> Dict[str, ValidationResult]:
        """Validate all domains in a collection"""
        with self._time_operation("validate_domain_collection"):
            results = {}
            
            # Validate each domain individually
            for domain_name, domain in domains.items():
                context = {'all_domains': domains}
                results[domain_name] = self.validate_domain(domain, context)
            
            return results
    
    def check_consistency(self, domains: DomainCollection) -> List[HealthIssue]:
        """Check cross-domain consistency"""
        with self._time_operation("check_consistency"):
            self.consistency_checks_performed += 1
            
            context = {'validator': self}
            all_issues = []
            
            # Run all consistency checks
            for check in self._consistency_checks:
                try:
                    issues = check.check(domains, context)
                    all_issues.extend(issues)
                except Exception as e:
                    self.logger.error(f"Consistency check '{check.name}' failed: {e}")
                    all_issues.append(HealthIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.VALIDATION,
                        description=f"Consistency check error: {str(e)}",
                        suggested_fix="Check consistency check implementation"
                    ))
            
            self.issues_found += len(all_issues)
            return all_issues
    
    def detect_circular_dependencies(self, domains: DomainCollection) -> List[List[str]]:
        """Detect circular dependencies between domains"""
        with self._time_operation("detect_circular_dependencies"):
            circular_deps = []
            visited = set()
            rec_stack = set()
            
            def dfs(domain_name: str, path: List[str]) -> bool:
                if domain_name in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(domain_name)
                    cycle = path[cycle_start:] + [domain_name]
                    circular_deps.append(cycle)
                    return True
                
                if domain_name in visited:
                    return False
                
                visited.add(domain_name)
                rec_stack.add(domain_name)
                
                domain = domains.get(domain_name)
                if domain:
                    for dep in domain.dependencies:
                        if dep in domains:  # Only check dependencies that exist
                            if dfs(dep, path + [domain_name]):
                                return True
                
                rec_stack.remove(domain_name)
                return False
            
            # Check each domain
            for domain_name in domains:
                if domain_name not in visited:
                    dfs(domain_name, [])
            
            return circular_deps
    
    def validate_dependencies(self, domains: DomainCollection) -> List[HealthIssue]:
        """Validate all domain dependencies"""
        with self._time_operation("validate_dependencies"):
            issues = []
            
            for domain_name, domain in domains.items():
                for dep in domain.dependencies:
                    if dep not in domains:
                        issues.append(HealthIssue(
                            severity=IssueSeverity.CRITICAL,
                            category=IssueCategory.DEPENDENCY,
                            description=f"Domain '{domain_name}' depends on non-existent domain '{dep}'",
                            suggested_fix=f"Either create domain '{dep}' or remove dependency",
                            affected_files=[domain_name]
                        ))
            
            # Check for circular dependencies
            circular_deps = self.detect_circular_dependencies(domains)
            for cycle in circular_deps:
                cycle_str = " -> ".join(cycle)
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.DEPENDENCY,
                    description=f"Circular dependency detected: {cycle_str}",
                    suggested_fix="Refactor to remove circular dependency",
                    affected_files=cycle[:-1]  # Exclude duplicate last element
                ))
            
            return issues
    
    def validate_file_patterns(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
        """Validate domain file patterns"""
        issues = []
        
        if not domain.patterns:
            issues.append(HealthIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.PATTERN,
                description=f"Domain '{domain.name}' has no file patterns",
                suggested_fix="Add at least one file pattern to define domain scope"
            ))
            return issues
        
        for pattern in domain.patterns:
            # Check pattern syntax
            if not isinstance(pattern, str) or not pattern.strip():
                issues.append(HealthIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.PATTERN,
                    description=f"Invalid pattern in domain '{domain.name}': {pattern}",
                    suggested_fix="Ensure all patterns are non-empty strings"
                ))
                continue
            
            # Check for common pattern issues
            if pattern.startswith('/'):
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.PATTERN,
                    description=f"Pattern '{pattern}' starts with '/' (absolute path)",
                    suggested_fix="Use relative paths for better portability"
                ))
            
            if '\\' in pattern:
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.PATTERN,
                    description=f"Pattern '{pattern}' uses backslashes",
                    suggested_fix="Use forward slashes for cross-platform compatibility"
                ))
            
            # Check if pattern exists on filesystem (if enabled)
            if self.check_filesystem:
                if not self._pattern_has_matches(pattern):
                    issues.append(HealthIssue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.PATTERN,
                        description=f"Pattern '{pattern}' matches no files",
                        suggested_fix="Verify pattern is correct or files exist"
                    ))
        
        return issues
    
    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add custom validation rule"""
        self._validation_rules.append(rule)
        self.logger.info(f"Added validation rule: {rule.name}")
    
    def add_consistency_check(self, check: ConsistencyCheck) -> None:
        """Add custom consistency check"""
        self._consistency_checks.append(check)
        self.logger.info(f"Added consistency check: {check.name}")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'validations_performed': self.validations_performed,
            'consistency_checks_performed': self.consistency_checks_performed,
            'issues_found': self.issues_found,
            'validation_rules_count': len(self._validation_rules),
            'consistency_checks_count': len(self._consistency_checks),
            'strict_mode': self.strict_mode,
            'check_filesystem': self.check_filesystem,
            'max_dependency_depth': self.max_dependency_depth
        }
    
    def _initialize_builtin_rules(self) -> None:
        """Initialize built-in validation rules"""
        
        # Required fields validation
        def validate_required_fields(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
            issues = []
            for field in self.required_fields:
                if not hasattr(domain, field) or not getattr(domain, field):
                    issues.append(HealthIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.VALIDATION,
                        description=f"Domain '{domain.name}' missing required field: {field}",
                        suggested_fix=f"Add {field} to domain definition"
                    ))
            return issues
        
        self._validation_rules.append(ValidationRule(
            name="required_fields",
            description="Validate required domain fields",
            severity=IssueSeverity.CRITICAL,
            category=IssueCategory.VALIDATION,
            validator_func=validate_required_fields
        ))
        
        # Domain name validation
        def validate_domain_name(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
            issues = []
            
            if not domain.name:
                issues.append(HealthIssue(
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.VALIDATION,
                    description="Domain name is empty",
                    suggested_fix="Provide a valid domain name"
                ))
                return issues
            
            # Check name format
            if not re.match(r'^[a-z][a-z0-9_]*$', domain.name):
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.VALIDATION,
                    description=f"Domain name '{domain.name}' doesn't follow naming convention",
                    suggested_fix="Use lowercase letters, numbers, and underscores only"
                ))
            
            # Check for reserved names
            reserved_names = {'test', 'temp', 'tmp', 'debug', 'admin'}
            if domain.name.lower() in reserved_names:
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.VALIDATION,
                    description=f"Domain name '{domain.name}' is reserved",
                    suggested_fix="Choose a more descriptive domain name"
                ))
            
            return issues
        
        self._validation_rules.append(ValidationRule(
            name="domain_name",
            description="Validate domain name format and conventions",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.VALIDATION,
            validator_func=validate_domain_name
        ))
        
        # File patterns validation
        self._validation_rules.append(ValidationRule(
            name="file_patterns",
            description="Validate domain file patterns",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.PATTERN,
            validator_func=self.validate_file_patterns
        ))
        
        # Tools validation
        def validate_tools(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
            issues = []
            
            if not domain.tools:
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.VALIDATION,
                    description=f"Domain '{domain.name}' has no tools configuration",
                    suggested_fix="Add tools configuration for linting, formatting, etc."
                ))
                return issues
            
            # Check for empty tool configurations
            if not domain.tools.linter:
                issues.append(HealthIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.VALIDATION,
                    description=f"Domain '{domain.name}' has no linter configured",
                    suggested_fix="Configure a linter for code quality"
                ))
            
            if not domain.tools.formatter:
                issues.append(HealthIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.VALIDATION,
                    description=f"Domain '{domain.name}' has no formatter configured",
                    suggested_fix="Configure a formatter for consistent code style"
                ))
            
            return issues
        
        self._validation_rules.append(ValidationRule(
            name="tools_validation",
            description="Validate domain tools configuration",
            severity=IssueSeverity.INFO,
            category=IssueCategory.VALIDATION,
            validator_func=validate_tools
        ))
    
    def _initialize_builtin_consistency_checks(self) -> None:
        """Initialize built-in consistency checks"""
        
        # Dependency consistency
        def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
            return self.validate_dependencies(domains)
        
        self._consistency_checks.append(ConsistencyCheck(
            name="dependency_consistency",
            description="Check domain dependency consistency",
            severity=IssueSeverity.CRITICAL,
            checker_func=check_dependency_consistency
        ))
        
        # Pattern overlap detection
        def check_pattern_overlaps(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
            issues = []
            domain_patterns = {}
            
            # Collect all patterns
            for domain_name, domain in domains.items():
                domain_patterns[domain_name] = domain.patterns
            
            # Check for overlaps
            for domain1, patterns1 in domain_patterns.items():
                for domain2, patterns2 in domain_patterns.items():
                    if domain1 >= domain2:  # Avoid duplicate checks
                        continue
                    
                    for pattern1 in patterns1:
                        for pattern2 in patterns2:
                            if self._patterns_overlap(pattern1, pattern2):
                                issues.append(HealthIssue(
                                    severity=IssueSeverity.WARNING,
                                    category=IssueCategory.PATTERN,
                                    description=f"Pattern overlap between '{domain1}' and '{domain2}': '{pattern1}' vs '{pattern2}'",
                                    suggested_fix="Review domain boundaries to avoid pattern conflicts",
                                    affected_files=[domain1, domain2]
                                ))
            
            return issues
        
        self._consistency_checks.append(ConsistencyCheck(
            name="pattern_overlaps",
            description="Check for overlapping file patterns between domains",
            severity=IssueSeverity.WARNING,
            checker_func=check_pattern_overlaps
        ))
        
        # Orphaned dependencies
        def check_orphaned_dependencies(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
            issues = []
            all_dependencies = set()
            domain_names = set(domains.keys())
            
            # Collect all dependencies
            for domain in domains.values():
                all_dependencies.update(domain.dependencies)
            
            # Find orphaned dependencies
            orphaned = all_dependencies - domain_names
            for orphan in orphaned:
                issues.append(HealthIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.DEPENDENCY,
                    description=f"Dependency '{orphan}' is referenced but no domain exists",
                    suggested_fix=f"Create domain '{orphan}' or remove references to it"
                ))
            
            return issues
        
        self._consistency_checks.append(ConsistencyCheck(
            name="orphaned_dependencies",
            description="Check for dependencies that don't correspond to existing domains",
            severity=IssueSeverity.WARNING,
            checker_func=check_orphaned_dependencies
        ))
    
    def _pattern_has_matches(self, pattern: str) -> bool:
        """Check if a pattern matches any files on the filesystem"""
        try:
            import glob
            matches = glob.glob(pattern, recursive=True)
            return len(matches) > 0
        except Exception:
            return True  # Assume valid if we can't check
    
    def _patterns_overlap(self, pattern1: str, pattern2: str) -> bool:
        """Check if two patterns might overlap"""
        # Simple overlap detection - could be enhanced
        # Remove wildcards for basic comparison
        base1 = pattern1.replace('**', '').replace('*', '').replace('//', '/')
        base2 = pattern2.replace('**', '').replace('*', '').replace('//', '/')
        
        # Check if one is a substring of the other
        return (base1 in base2 or base2 in base1) and base1 != base2


class SchemaValidator:
    """JSON Schema validator for domain structures"""
    
    def __init__(self):
        self.domain_schema = {
            "type": "object",
            "required": ["name", "description", "patterns", "tools", "metadata"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9_]*$",
                    "minLength": 1
                },
                "description": {
                    "type": "string",
                    "minLength": 10
                },
                "patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "content_indicators": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "requirements": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "tools": {
                    "type": "object",
                    "required": ["linter", "formatter", "validator"],
                    "properties": {
                        "linter": {"type": "string"},
                        "formatter": {"type": "string"},
                        "validator": {"type": "string"},
                        "exclusions": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "required": ["demo_role", "extraction_candidate", "package_potential"],
                    "properties": {
                        "demo_role": {"type": "string"},
                        "extraction_candidate": {
                            "type": "string",
                            "enum": ["yes", "no", "maybe", "unknown"]
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "deprecated", "planned", "archived"]
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def validate_schema(self, domain_dict: Dict[str, Any]) -> List[str]:
        """Validate domain dictionary against schema"""
        try:
            import jsonschema
            jsonschema.validate(domain_dict, self.domain_schema)
            return []
        except ImportError:
            # Fallback to basic validation if jsonschema not available
            return self._basic_schema_validation(domain_dict)
        except jsonschema.ValidationError as e:
            return [str(e)]
    
    def _basic_schema_validation(self, domain_dict: Dict[str, Any]) -> List[str]:
        """Basic schema validation without jsonschema library"""
        errors = []
        
        # Check required fields
        required_fields = ["name", "description", "patterns", "tools", "metadata"]
        for field in required_fields:
            if field not in domain_dict:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        if "name" in domain_dict and not isinstance(domain_dict["name"], str):
            errors.append("Field 'name' must be a string")
        
        if "patterns" in domain_dict and not isinstance(domain_dict["patterns"], list):
            errors.append("Field 'patterns' must be an array")
        
        return errors