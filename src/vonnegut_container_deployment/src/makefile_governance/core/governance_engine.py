"""
Makefile Governance Engine

Enforces makefile quality standards, naming conventions, and complexity limits.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth


class GovernanceRuleType(Enum):
    """Types of governance rules."""
    NAMING_CONVENTION = "naming_convention"
    COMPLEXITY_LIMIT = "complexity_limit"
    PHONY_DECLARATION = "phony_declaration"
    ENVIRONMENT_VARIABLE = "environment_variable"
    EXTERNAL_SCRIPT = "external_script"
    TARGET_DESCRIPTION = "target_description"


class ViolationSeverity(Enum):
    """Severity levels for governance violations."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class GovernanceRule:
    """Represents a governance rule."""
    rule_type: GovernanceRuleType
    name: str
    description: str
    severity: ViolationSeverity
    enabled: bool = True
    parameters: Dict[str, Any] = None


@dataclass
class GovernanceViolation:
    """Represents a governance rule violation."""
    rule: GovernanceRule
    line_number: int
    line_content: str
    message: str
    suggested_fix: Optional[str] = None
    target_name: Optional[str] = None


@dataclass
class GovernanceResult:
    """Result of governance validation."""
    is_compliant: bool
    violations: List[GovernanceViolation]
    complexity_score: float
    quality_score: float
    recommendations: List[str]


class MakefileGovernanceEngine(ReflectiveModule):
    """
    Makefile governance engine for enforcing quality standards.
    
    Validates naming conventions, complexity limits, and best practices
    for makefile development within the Beast Mode Framework.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "makefile_governance_engine"
        self._logger = logging.getLogger(__name__)
        
        # Initialize governance rules
        self._rules = self._initialize_default_rules()
        
        # Statistics
        self._validation_count = 0
        self._violation_count = 0
        self._compliance_rate = 1.0
        
        # Patterns for validation
        self._kebab_case_pattern = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
        self._target_pattern = re.compile(r'^([^:]+):\s*(.*)$')
        self._phony_pattern = re.compile(r'^\.PHONY:\s*(.+)$')
        self._env_var_pattern = re.compile(r'\$\(([A-Z_][A-Z0-9_]*)\)')
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Governance Engine",
            "version": "1.0.0",
            "description": "Enforces makefile quality standards and best practices",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "statistics": {
                "validations_performed": self._validation_count,
                "violations_detected": self._violation_count,
                "compliance_rate": self._compliance_rate
            },
            "rules": {
                "total_rules": len(self._rules),
                "enabled_rules": len([r for r in self._rules if r.enabled])
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.CORE_FUNCTIONALITY
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        # Calculate health score based on compliance rate
        if self._compliance_rate >= 0.9:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif self._compliance_rate >= 0.7:
            status = ModuleStatus.WARNING
            health_score = 0.7
        else:
            status = ModuleStatus.ERROR
            health_score = 0.3
        
        issues = []
        if self._compliance_rate < 0.9:
            issues.append(f"Compliance rate below threshold: {self._compliance_rate:.2%}")
        if self._violation_count > 0:
            issues.append(f"Detected {self._violation_count} governance violations")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=0,
            warning_count=len([r for r in self._rules if not r.enabled])
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        # In degraded mode, only enforce critical rules
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
            remaining_capabilities=[ModuleCapability.VALIDATION, ModuleCapability.CORE_FUNCTIONALITY],
            error_message=None
        )
    
    def validate_governance(self, file_path: Path) -> GovernanceResult:
        """
        Validate makefile against governance rules.
        
        Args:
            file_path: Path to the makefile to validate
            
        Returns:
            GovernanceResult with violations and quality metrics
        """
        with self.trace_operation("validate_governance", file_path=str(file_path)) as trace:
            self._validation_count += 1
            self._update_activity()
            
            try:
                if not file_path.exists():
                    violation = GovernanceViolation(
                        rule=self._get_rule_by_type(GovernanceRuleType.NAMING_CONVENTION),
                        line_number=0,
                        line_content="",
                        message=f"Makefile not found: {file_path}"
                    )
                    return GovernanceResult(
                        is_compliant=False,
                        violations=[violation],
                        complexity_score=0.0,
                        quality_score=0.0,
                        recommendations=[]
                    )
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                violations = []
                
                # Apply all enabled governance rules
                for rule in self._rules:
                    if rule.enabled:
                        rule_violations = self._apply_rule(rule, content, file_path)
                        violations.extend(rule_violations)
                
                # Calculate metrics
                complexity_score = self._calculate_complexity_score(content)
                quality_score = self._calculate_quality_score(content, violations)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(violations, complexity_score)
                
                # Update statistics
                self._violation_count += len(violations)
                if self._validation_count > 0:
                    self._compliance_rate = 1.0 - (self._violation_count / self._validation_count)
                
                is_compliant = len([v for v in violations if v.rule.severity in [ViolationSeverity.ERROR, ViolationSeverity.CRITICAL]]) == 0
                
                result = GovernanceResult(
                    is_compliant=is_compliant,
                    violations=violations,
                    complexity_score=complexity_score,
                    quality_score=quality_score,
                    recommendations=recommendations
                )
                
                trace.output_result = {
                    "is_compliant": is_compliant,
                    "violation_count": len(violations),
                    "complexity_score": complexity_score,
                    "quality_score": quality_score
                }
                
                return result
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Governance validation failed for {file_path}: {e}")
                raise
    
    def _initialize_default_rules(self) -> List[GovernanceRule]:
        """Initialize default governance rules."""
        return [
            GovernanceRule(
                rule_type=GovernanceRuleType.NAMING_CONVENTION,
                name="kebab_case_targets",
                description="Target names should use kebab-case convention",
                severity=ViolationSeverity.WARNING,
                parameters={"pattern": "kebab-case"}
            ),
            GovernanceRule(
                rule_type=GovernanceRuleType.PHONY_DECLARATION,
                name="phony_declarations",
                description="Side-effect targets should be declared as .PHONY",
                severity=ViolationSeverity.WARNING
            ),
            GovernanceRule(
                rule_type=GovernanceRuleType.COMPLEXITY_LIMIT,
                name="recipe_complexity",
                description="Complex recipes (>3 lines) should use external scripts",
                severity=ViolationSeverity.INFO,
                parameters={"max_lines": 3}
            ),
            GovernanceRule(
                rule_type=GovernanceRuleType.ENVIRONMENT_VARIABLE,
                name="env_var_validation",
                description="Environment variables should follow naming conventions",
                severity=ViolationSeverity.WARNING
            ),
            GovernanceRule(
                rule_type=GovernanceRuleType.TARGET_DESCRIPTION,
                name="target_descriptions",
                description="Targets should have descriptive comments",
                severity=ViolationSeverity.INFO
            )
        ]
    
    def _get_rule_by_type(self, rule_type: GovernanceRuleType) -> GovernanceRule:
        """Get rule by type."""
        for rule in self._rules:
            if rule.rule_type == rule_type:
                return rule
        
        # Return a default rule if not found
        return GovernanceRule(
            rule_type=rule_type,
            name="default",
            description="Default rule",
            severity=ViolationSeverity.WARNING
        )
    
    def _apply_rule(self, rule: GovernanceRule, content: str, file_path: Path) -> List[GovernanceViolation]:
        """Apply a specific governance rule."""
        violations = []
        
        if rule.rule_type == GovernanceRuleType.NAMING_CONVENTION:
            violations.extend(self._check_naming_convention(rule, content))
        elif rule.rule_type == GovernanceRuleType.PHONY_DECLARATION:
            violations.extend(self._check_phony_declarations(rule, content))
        elif rule.rule_type == GovernanceRuleType.COMPLEXITY_LIMIT:
            violations.extend(self._check_complexity_limit(rule, content))
        elif rule.rule_type == GovernanceRuleType.ENVIRONMENT_VARIABLE:
            violations.extend(self._check_environment_variables(rule, content))
        elif rule.rule_type == GovernanceRuleType.TARGET_DESCRIPTION:
            violations.extend(self._check_target_descriptions(rule, content))
        
        return violations
    
    def _check_naming_convention(self, rule: GovernanceRule, content: str) -> List[GovernanceViolation]:
        """Check target naming conventions."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            target_match = self._target_pattern.match(line)
            
            if target_match:
                target_name = target_match.group(1).strip()
                
                # Skip special targets
                if target_name.startswith('.') or target_name in ['%']:
                    continue
                
                # Check kebab-case convention
                if not self._kebab_case_pattern.match(target_name):
                    violations.append(GovernanceViolation(
                        rule=rule,
                        line_number=i,
                        line_content=line,
                        message=f"Target '{target_name}' should use kebab-case naming convention",
                        suggested_fix=self._suggest_kebab_case(target_name),
                        target_name=target_name
                    ))
        
        return violations
    
    def _check_phony_declarations(self, rule: GovernanceRule, content: str) -> List[GovernanceViolation]:
        """Check for missing .PHONY declarations."""
        violations = []
        lines = content.split('\n')
        
        # Extract targets and PHONY declarations
        targets = []
        phony_targets = set()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Extract targets
            target_match = self._target_pattern.match(line)
            if target_match:
                target_name = target_match.group(1).strip()
                if not target_name.startswith('.'):
                    targets.append((target_name, i, line))
            
            # Extract PHONY declarations
            phony_match = self._phony_pattern.match(line)
            if phony_match:
                phony_list = phony_match.group(1).split()
                phony_targets.update(phony_list)
        
        # Check for missing PHONY declarations
        for target_name, line_num, line_content in targets:
            if self._should_be_phony(target_name) and target_name not in phony_targets:
                violations.append(GovernanceViolation(
                    rule=rule,
                    line_number=line_num,
                    line_content=line_content,
                    message=f"Target '{target_name}' should be declared as .PHONY",
                    suggested_fix=f".PHONY: {target_name}",
                    target_name=target_name
                ))
        
        return violations
    
    def _check_complexity_limit(self, rule: GovernanceRule, content: str) -> List[GovernanceViolation]:
        """Check for overly complex recipes."""
        violations = []
        lines = content.split('\n')
        
        max_lines = rule.parameters.get("max_lines", 3) if rule.parameters else 3
        current_target = None
        current_target_line = 0
        recipe_lines = []
        
        for i, line in enumerate(lines, 1):
            # Check if this is a target line
            if ':' in line and not line.startswith('\t'):
                # Process previous target if it exists
                if current_target and len(recipe_lines) > max_lines:
                    violations.append(GovernanceViolation(
                        rule=rule,
                        line_number=current_target_line,
                        line_content=current_target,
                        message=f"Recipe has {len(recipe_lines)} lines (>{max_lines}), consider using external script",
                        suggested_fix=f"Consider moving complex logic to scripts/ directory",
                        target_name=current_target.split(':')[0].strip()
                    ))
                
                # Start tracking new target
                target_match = self._target_pattern.match(line.strip())
                if target_match:
                    current_target = line.strip()
                    current_target_line = i
                    recipe_lines = []
            
            # Count recipe lines (start with tab)
            elif line.startswith('\t') and current_target:
                recipe_lines.append(line)
        
        # Check the last target
        if current_target and len(recipe_lines) > max_lines:
            violations.append(GovernanceViolation(
                rule=rule,
                line_number=current_target_line,
                line_content=current_target,
                message=f"Recipe has {len(recipe_lines)} lines (>{max_lines}), consider using external script",
                suggested_fix=f"Consider moving complex logic to scripts/ directory",
                target_name=current_target.split(':')[0].strip()
            ))
        
        return violations
    
    def _check_environment_variables(self, rule: GovernanceRule, content: str) -> List[GovernanceViolation]:
        """Check environment variable usage."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Find environment variable references
            for match in self._env_var_pattern.finditer(line):
                var_name = match.group(1)
                
                # Check naming convention (should be UPPER_SNAKE_CASE)
                if not re.match(r'^[A-Z_][A-Z0-9_]*$', var_name):
                    violations.append(GovernanceViolation(
                        rule=rule,
                        line_number=i,
                        line_content=line.strip(),
                        message=f"Environment variable '{var_name}' should use UPPER_SNAKE_CASE",
                        suggested_fix=f"Use {var_name.upper().replace('-', '_')} instead"
                    ))
        
        return violations
    
    def _check_target_descriptions(self, rule: GovernanceRule, content: str) -> List[GovernanceViolation]:
        """Check for target descriptions."""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            target_match = self._target_pattern.match(line_stripped)
            
            if target_match:
                target_name = target_match.group(1).strip()
                
                # Skip special targets
                if target_name.startswith('.'):
                    continue
                
                # Check if target has description (## comment)
                if '##' not in line:
                    violations.append(GovernanceViolation(
                        rule=rule,
                        line_number=i,
                        line_content=line_stripped,
                        message=f"Target '{target_name}' should have a description comment (##)",
                        suggested_fix=f"{target_name}: ## Add description here",
                        target_name=target_name
                    ))
        
        return violations
    
    def _should_be_phony(self, target_name: str) -> bool:
        """Check if a target should be declared as PHONY."""
        phony_keywords = [
            'help', 'clean', 'test', 'install', 'deploy', 'build',
            'run', 'start', 'stop', 'restart', 'status', 'check',
            'lint', 'format', 'validate', 'setup', 'init'
        ]
        
        return any(keyword in target_name.lower() for keyword in phony_keywords)
    
    def _suggest_kebab_case(self, target_name: str) -> str:
        """Suggest kebab-case version of target name."""
        # Convert to lowercase and replace underscores/spaces with hyphens
        suggested = target_name.lower()
        suggested = re.sub(r'[_\s]+', '-', suggested)
        suggested = re.sub(r'[^a-z0-9-]', '', suggested)
        suggested = re.sub(r'-+', '-', suggested)
        suggested = suggested.strip('-')
        
        return suggested
    
    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate complexity score for the makefile."""
        lines = content.split('\n')
        
        # Count various complexity factors
        target_count = 0
        recipe_line_count = 0
        variable_count = 0
        dependency_count = 0
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Count targets
            if ':' in line and not line.startswith('\t'):
                target_count += 1
                # Count dependencies
                deps = line.split(':', 1)[1].strip()
                if deps:
                    dependency_count += len(deps.split())
            
            # Count recipe lines
            elif line.startswith('\t'):
                recipe_line_count += 1
            
            # Count variables
            elif '=' in line:
                variable_count += 1
        
        # Calculate complexity score (0-1, lower is better)
        complexity_factors = [
            min(target_count / 20, 1.0),  # Normalize to 20 targets
            min(recipe_line_count / 100, 1.0),  # Normalize to 100 recipe lines
            min(variable_count / 30, 1.0),  # Normalize to 30 variables
            min(dependency_count / 50, 1.0)  # Normalize to 50 dependencies
        ]
        
        return sum(complexity_factors) / len(complexity_factors)
    
    def _calculate_quality_score(self, content: str, violations: List[GovernanceViolation]) -> float:
        """Calculate quality score for the makefile."""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            ViolationSeverity.INFO: 0.1,
            ViolationSeverity.WARNING: 0.3,
            ViolationSeverity.ERROR: 0.7,
            ViolationSeverity.CRITICAL: 1.0
        }
        
        total_weight = sum(severity_weights[v.rule.severity] for v in violations)
        
        # Calculate score (0-1, higher is better)
        lines_count = len([line for line in content.split('\n') if line.strip()])
        if lines_count == 0:
            return 0.0
        
        # Normalize by content size
        penalty = total_weight / max(lines_count / 10, 1.0)
        quality_score = max(0.0, 1.0 - penalty)
        
        return quality_score
    
    def _generate_recommendations(self, violations: List[GovernanceViolation], complexity_score: float) -> List[str]:
        """Generate recommendations based on violations and complexity."""
        recommendations = []
        
        # Group violations by type
        violation_types = {}
        for violation in violations:
            rule_type = violation.rule.rule_type
            if rule_type not in violation_types:
                violation_types[rule_type] = []
            violation_types[rule_type].append(violation)
        
        # Generate type-specific recommendations
        if GovernanceRuleType.NAMING_CONVENTION in violation_types:
            count = len(violation_types[GovernanceRuleType.NAMING_CONVENTION])
            recommendations.append(f"Consider renaming {count} targets to use kebab-case convention")
        
        if GovernanceRuleType.PHONY_DECLARATION in violation_types:
            count = len(violation_types[GovernanceRuleType.PHONY_DECLARATION])
            recommendations.append(f"Add .PHONY declarations for {count} side-effect targets")
        
        if GovernanceRuleType.COMPLEXITY_LIMIT in violation_types:
            count = len(violation_types[GovernanceRuleType.COMPLEXITY_LIMIT])
            recommendations.append(f"Move {count} complex recipes to external scripts")
        
        if GovernanceRuleType.TARGET_DESCRIPTION in violation_types:
            count = len(violation_types[GovernanceRuleType.TARGET_DESCRIPTION])
            recommendations.append(f"Add descriptive comments to {count} targets")
        
        # Complexity-based recommendations
        if complexity_score > 0.7:
            recommendations.append("Consider breaking down this makefile into smaller, modular files")
        
        if complexity_score > 0.5:
            recommendations.append("Consider using include directives to organize related targets")
        
        return recommendations
    
    def get_governance_rules(self) -> List[GovernanceRule]:
        """Get all governance rules."""
        return self._rules.copy()
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a governance rule."""
        for rule in self._rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a governance rule."""
        for rule in self._rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False
    
    def add_custom_rule(self, rule: GovernanceRule) -> None:
        """Add a custom governance rule."""
        self._rules.append(rule)