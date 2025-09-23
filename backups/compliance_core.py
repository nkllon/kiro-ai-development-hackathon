"""
Compliance Core

This module was extracted from compliance.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING
from enum import Enum
from ..models import ComplianceReport, DomainException
from .base import ReflectiveModuleBase, DomainReflectiveModule
from .registry import get_global_registry


class ValidationSeverity(Enum):
    """Severity levels for validation results."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    code: str
    message: str
    severity: ValidationSeverity
    component: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_blocking(self) -> bool:
        """Check if this issue blocks compliance."""
        return self.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]


@dataclass
class ValidationResult:
    """
    Result of a compliance validation operation.

    Contains all validation issues found during compliance checking,
    categorized by severity level.
    """

    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    validator_id: Optional[str] = None

    @property
    def errors(self) -> List[str]:
        """Get list of error messages."""
        return [
            issue.message
            for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self) -> List[str]:
        """Get list of warning messages."""
        return [
            issue.message
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]

    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get list of critical issues."""
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.CRITICAL
        ]

    @property
    def blocking_issues(self) -> List[ValidationIssue]:
        """Get list of issues that block compliance."""
        return [issue for issue in self.issues if issue.is_blocking]

    def add_error(
        self,
        message: str,
        code: str = "VALIDATION_ERROR",
        component: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ):
        """Add a validation error."""
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=ValidationSeverity.ERROR,
                component=component,
                context=context or {},
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        message: str,
        code: str = "VALIDATION_WARNING",
        component: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ):
        """Add a validation warning."""
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=ValidationSeverity.WARNING,
                component=component,
                context=context or {},
            )
        )

    def add_critical(
        self,
        message: str,
        code: str = "VALIDATION_CRITICAL",
        component: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ):
        """Add a critical validation issue."""
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=ValidationSeverity.CRITICAL,
                component=component,
                context=context or {},
            )
        )
        self.is_valid = False

    def merge(self, other: "ValidationResult"):
        """Merge another validation result into this one."""
        self.issues.extend(other.issues)
        if not other.is_valid:
            self.is_valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "timestamp": self.timestamp.isoformat(),
            "validator_id": self.validator_id,
            "issue_count": len(self.issues),
            "error_count": len(
                [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
            ),
            "warning_count": len(
                [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
            ),
            "critical_count": len(
                [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
            ),
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "severity": issue.severity.value,
                    "component": issue.component,
                    "context": issue.context,
                    "timestamp": issue.timestamp.isoformat(),
                }
                for issue in self.issues
            ],
        }


class ComplianceValidator(ABC):
    """
    Abstract base class for compliance validators.

    Provides the framework for implementing specific compliance validators
    for different standards (RM compliance, DDD patterns, regulatory requirements).
    """

    def __init__(self, validator_id: str):
        """
        Initialize compliance validator.

        Args:
            validator_id: Unique identifier for this validator
        """
        self.validator_id = validator_id
        self._validation_rules: Dict[str, Any] = {}

    @abstractmethod
    async def validate(self, component: "ReflectiveModuleBase") -> ValidationResult:
        """
        Validate a component for compliance.

        Args:
            component: The RM component to validate

        Returns:
            ValidationResult containing all validation issues found
        """
        pass

    def add_validation_rule(self, rule_id: str, rule_config: Dict[str, Any]):
        """Add a validation rule to this validator."""
        self._validation_rules[rule_id] = rule_config

    def remove_validation_rule(self, rule_id: str):
        """Remove a validation rule from this validator."""
        self._validation_rules.pop(rule_id, None)

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get all validation rules for this validator."""
        return self._validation_rules.copy()


class RMComplianceValidator(ComplianceValidator):
    """
    Validator for Reflective Module (RM) compliance.

    Ensures that all RM components properly implement the RM interface
    and follow RM architectural patterns.
    """

    def __init__(self):
        super().__init__("rm_compliance_validator")
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default RM compliance rules."""
        self.add_validation_rule(
            "module_id_required",
            {"description": "Module must have a valid module_id", "severity": "error"},
        )
        self.add_validation_rule(
            "health_check_implemented",
            {
                "description": "Module must implement health check methods",
                "severity": "error",
            },
        )
        self.add_validation_rule(
            "capabilities_defined",
            {
                "description": "Module must define its capabilities",
                "severity": "warning",
            },
        )
        self.add_validation_rule(
            "registry_integration",
            {
                "description": "Module must integrate with global registry",
                "severity": "error",
            },
        )

    async def validate(self, component: "ReflectiveModuleBase") -> ValidationResult:
        """Validate RM compliance for a component."""
        result = ValidationResult(validator_id=self.validator_id)
        if not hasattr(component, "module_id") or not component.module_id:
            result.add_error(
                "Module must have a valid module_id",
                code="RM_001",
                component=component.__class__.__name__,
            )
        try:
            health_status = await component.get_module_status()
            if not health_status:
                result.add_error(
                    "get_module_status() must return valid ModuleHealth",
                    code="RM_002",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "get_module_status() method not implemented",
                code="RM_002",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"get_module_status() failed: {str(e)}",
                code="RM_002",
                component=component.__class__.__name__,
            )
        try:
            capabilities = await component.get_module_capabilities()
            if not capabilities:
                result.add_warning(
                    "Module should define at least one capability",
                    code="RM_003",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "get_module_capabilities() method not implemented",
                code="RM_003",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"get_module_capabilities() failed: {str(e)}",
                code="RM_003",
                component=component.__class__.__name__,
            )
        try:
            is_healthy = await component.is_healthy()
            if not isinstance(is_healthy, bool):
                result.add_error(
                    "is_healthy() must return boolean value",
                    code="RM_004",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "is_healthy() method not implemented",
                code="RM_004",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"is_healthy() failed: {str(e)}",
                code="RM_004",
                component=component.__class__.__name__,
            )
        try:
            indicators = await component.get_health_indicators()
            if not isinstance(indicators, dict):
                result.add_error(
                    "get_health_indicators() must return dictionary",
                    code="RM_005",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "get_health_indicators() method not implemented",
                code="RM_005",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"get_health_indicators() failed: {str(e)}",
                code="RM_005",
                component=component.__class__.__name__,
            )
        return result


class DDDComplianceValidator(ComplianceValidator):
    """
    Validator for Domain-Driven Design (DDD) compliance.

    Ensures that domain components properly implement DDD patterns
    and follow domain modeling best practices.
    """

    def __init__(self):
        super().__init__("ddd_compliance_validator")
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default DDD compliance rules."""
        self.add_validation_rule(
            "domain_boundaries_defined",
            {
                "description": "Domain components must define clear boundaries",
                "severity": "error",
            },
        )
        self.add_validation_rule(
            "invariants_validated",
            {
                "description": "Domain components must validate invariants",
                "severity": "error",
            },
        )
        self.add_validation_rule(
            "ubiquitous_language",
            {
                "description": "Components should use ubiquitous language",
                "severity": "warning",
            },
        )
        self.add_validation_rule(
            "domain_context_specified",
            {
                "description": "Domain components must specify their context",
                "severity": "error",
            },
        )

    async def validate(self, component: "ReflectiveModuleBase") -> ValidationResult:
        """Validate DDD compliance for a component."""
        result = ValidationResult(validator_id=self.validator_id)
        if not hasattr(component, "domain_context"):
            return result
        domain_component = component
        if (
            not hasattr(domain_component, "domain_context")
            or not domain_component.domain_context
        ):
            result.add_error(
                "Domain component must specify domain_context",
                code="DDD_001",
                component=component.__class__.__name__,
            )
        try:
            boundaries = domain_component.get_domain_boundaries()
            if not boundaries:
                result.add_error(
                    "get_domain_boundaries() must return valid DomainBoundaries",
                    code="DDD_002",
                    component=component.__class__.__name__,
                )
            elif not boundaries.context:
                result.add_error(
                    "Domain boundaries must specify context",
                    code="DDD_002",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "get_domain_boundaries() method not implemented",
                code="DDD_002",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"get_domain_boundaries() failed: {str(e)}",
                code="DDD_002",
                component=component.__class__.__name__,
            )
        try:
            validation_result = domain_component.validate_domain_invariants()
            if not validation_result:
                result.add_error(
                    "validate_domain_invariants() must return ValidationResult",
                    code="DDD_003",
                    component=component.__class__.__name__,
                )
        except NotImplementedError:
            result.add_error(
                "validate_domain_invariants() method not implemented",
                code="DDD_003",
                component=component.__class__.__name__,
            )
        except Exception as e:
            result.add_error(
                f"validate_domain_invariants() failed: {str(e)}",
                code="DDD_003",
                component=component.__class__.__name__,
            )
        return result


class ComplianceOrchestrator:
    """
    Orchestrates compliance validation across multiple validators.

    Manages multiple compliance validators and provides comprehensive
    compliance reporting for RM components.
    """

    def __init__(self):
        """Initialize compliance orchestrator."""
        self._validators: Dict[str, ComplianceValidator] = {}
        self._compliance_standards: Set[str] = set()
        self.register_validator(RMComplianceValidator())
        self.register_validator(DDDComplianceValidator())

    def register_validator(self, validator: ComplianceValidator):
        """Register a compliance validator."""
        self._validators[validator.validator_id] = validator
        logger.info(f"Registered compliance validator: {validator.validator_id}")

    def unregister_validator(self, validator_id: str):
        """Unregister a compliance validator."""
        if validator_id in self._validators:
            del self._validators[validator_id]
            logger.info(f"Unregistered compliance validator: {validator_id}")

    def add_compliance_standard(self, standard: str):
        """Add a compliance standard to check."""
        self._compliance_standards.add(standard)

    def remove_compliance_standard(self, standard: str):
        """Remove a compliance standard."""
        self._compliance_standards.discard(standard)

    async def validate_component(
        self, component: "ReflectiveModuleBase"
    ) -> ComplianceReport:
        """
        Perform comprehensive compliance validation on a component.

        Args:
            component: The RM component to validate

        Returns:
            ComplianceReport containing all validation results
        """
        all_violations = []
        all_warnings = []
        for validator_id, validator in self._validators.items():
            try:
                validation_result = await validator.validate(component)
                for issue in validation_result.issues:
                    if issue.is_blocking:
                        all_violations.append(f"[{validator_id}] {issue.message}")
                    else:
                        all_warnings.append(f"[{validator_id}] {issue.message}")
            except Exception as e:
                logger.error(f"Validator {validator_id} failed: {e}")
                all_violations.append(
                    f"[{validator_id}] Validator execution failed: {str(e)}"
                )
        total_issues = len(all_violations) + len(all_warnings)
        if total_issues == 0:
            score = 100.0
        else:
            violation_weight = 10
            warning_weight = 1
            total_weight = (
                len(all_violations) * violation_weight
                + len(all_warnings) * warning_weight
            )
            max_weight = total_issues * violation_weight
            score = max(0.0, 100.0 - total_weight / max_weight * 100.0)
        return ComplianceReport(
            component_id=getattr(component, "module_id", "unknown"),
            compliance_standards=list(self._compliance_standards),
            violations=all_violations,
            warnings=all_warnings,
            score=score,
        )

    async def validate_system(self) -> Dict[str, ComplianceReport]:
        """
        Validate compliance for all registered components in the system.

        Returns:
            Dictionary mapping component IDs to their compliance reports
        """
        from .registry import get_global_registry

        registry = get_global_registry()
        all_modules = registry.get_all_modules()
        compliance_reports = {}
        for registered_module in all_modules:
            try:
                report = await self.validate_component(registered_module.module)
                compliance_reports[registered_module.module_id] = report
            except Exception as e:
                logger.error(
                    f"Failed to validate component {registered_module.module_id}: {e}"
                )
                compliance_reports[registered_module.module_id] = ComplianceReport(
                    component_id=registered_module.module_id,
                    compliance_standards=list(self._compliance_standards),
                    violations=[f"Validation failed: {str(e)}"],
                    score=0.0,
                )
        return compliance_reports

    def get_registered_validators(self) -> List[str]:
        """Get list of registered validator IDs."""
        return list(self._validators.keys())

    def get_compliance_standards(self) -> List[str]:
        """Get list of compliance standards being checked."""
        return list(self._compliance_standards)


def get_global_compliance_orchestrator() -> ComplianceOrchestrator:
    """Get the global compliance orchestrator instance."""
    global _global_compliance_orchestrator
    if _global_compliance_orchestrator is None:
        _global_compliance_orchestrator = ComplianceOrchestrator()
    return _global_compliance_orchestrator


@property
def is_blocking(self) -> bool:
    """Check if this issue blocks compliance."""
    return self.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]


@property
def errors(self) -> List[str]:
    """Get list of error messages."""
    return [
        issue.message
        for issue in self.issues
        if issue.severity == ValidationSeverity.ERROR
    ]


@property
def warnings(self) -> List[str]:
    """Get list of warning messages."""
    return [
        issue.message
        for issue in self.issues
        if issue.severity == ValidationSeverity.WARNING
    ]


@property
def critical_issues(self) -> List[ValidationIssue]:
    """Get list of critical issues."""
    return [
        issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL
    ]


@property
def blocking_issues(self) -> List[ValidationIssue]:
    """Get list of issues that block compliance."""
    return [issue for issue in self.issues if issue.is_blocking]


def add_error(
    self,
    message: str,
    code: str = "VALIDATION_ERROR",
    component: str = "unknown",
    context: Optional[Dict[str, Any]] = None,
):
    """Add a validation error."""
    self.issues.append(
        ValidationIssue(
            code=code,
            message=message,
            severity=ValidationSeverity.ERROR,
            component=component,
            context=context or {},
        )
    )
    self.is_valid = False


def add_warning(
    self,
    message: str,
    code: str = "VALIDATION_WARNING",
    component: str = "unknown",
    context: Optional[Dict[str, Any]] = None,
):
    """Add a validation warning."""
    self.issues.append(
        ValidationIssue(
            code=code,
            message=message,
            severity=ValidationSeverity.WARNING,
            component=component,
            context=context or {},
        )
    )


def add_critical(
    self,
    message: str,
    code: str = "VALIDATION_CRITICAL",
    component: str = "unknown",
    context: Optional[Dict[str, Any]] = None,
):
    """Add a critical validation issue."""
    self.issues.append(
        ValidationIssue(
            code=code,
            message=message,
            severity=ValidationSeverity.CRITICAL,
            component=component,
            context=context or {},
        )
    )
    self.is_valid = False


def merge(self, other: "ValidationResult"):
    """Merge another validation result into this one."""
    self.issues.extend(other.issues)
    if not other.is_valid:
        self.is_valid = False


def to_dict(self) -> Dict[str, Any]:
    """Convert validation result to dictionary."""
    return {
        "is_valid": self.is_valid,
        "timestamp": self.timestamp.isoformat(),
        "validator_id": self.validator_id,
        "issue_count": len(self.issues),
        "error_count": len(
            [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
        ),
        "warning_count": len(
            [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
        ),
        "critical_count": len(
            [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
        ),
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "severity": issue.severity.value,
                "component": issue.component,
                "context": issue.context,
                "timestamp": issue.timestamp.isoformat(),
            }
            for issue in self.issues
        ],
    }


def __init__(self, validator_id: str):
    """
    Initialize compliance validator.

    Args:
        validator_id: Unique identifier for this validator
    """
    self.validator_id = validator_id
    self._validation_rules: Dict[str, Any] = {}


def add_validation_rule(self, rule_id: str, rule_config: Dict[str, Any]):
    """Add a validation rule to this validator."""
    self._validation_rules[rule_id] = rule_config


def remove_validation_rule(self, rule_id: str):
    """Remove a validation rule from this validator."""
    self._validation_rules.pop(rule_id, None)


def get_validation_rules(self) -> Dict[str, Any]:
    """Get all validation rules for this validator."""
    return self._validation_rules.copy()


def __init__(self):
    super().__init__("rm_compliance_validator")
    self._setup_default_rules()


def _setup_default_rules(self):
    """Setup default RM compliance rules."""
    self.add_validation_rule(
        "module_id_required",
        {"description": "Module must have a valid module_id", "severity": "error"},
    )
    self.add_validation_rule(
        "health_check_implemented",
        {
            "description": "Module must implement health check methods",
            "severity": "error",
        },
    )
    self.add_validation_rule(
        "capabilities_defined",
        {"description": "Module must define its capabilities", "severity": "warning"},
    )
    self.add_validation_rule(
        "registry_integration",
        {
            "description": "Module must integrate with global registry",
            "severity": "error",
        },
    )


def __init__(self):
    super().__init__("ddd_compliance_validator")
    self._setup_default_rules()


def _setup_default_rules(self):
    """Setup default DDD compliance rules."""
    self.add_validation_rule(
        "domain_boundaries_defined",
        {
            "description": "Domain components must define clear boundaries",
            "severity": "error",
        },
    )
    self.add_validation_rule(
        "invariants_validated",
        {
            "description": "Domain components must validate invariants",
            "severity": "error",
        },
    )
    self.add_validation_rule(
        "ubiquitous_language",
        {
            "description": "Components should use ubiquitous language",
            "severity": "warning",
        },
    )
    self.add_validation_rule(
        "domain_context_specified",
        {
            "description": "Domain components must specify their context",
            "severity": "error",
        },
    )


def __init__(self):
    """Initialize compliance orchestrator."""
    self._validators: Dict[str, ComplianceValidator] = {}
    self._compliance_standards: Set[str] = set()
    self.register_validator(RMComplianceValidator())
    self.register_validator(DDDComplianceValidator())


def register_validator(self, validator: ComplianceValidator):
    """Register a compliance validator."""
    self._validators[validator.validator_id] = validator
    logger.info(f"Registered compliance validator: {validator.validator_id}")


def unregister_validator(self, validator_id: str):
    """Unregister a compliance validator."""
    if validator_id in self._validators:
        del self._validators[validator_id]
        logger.info(f"Unregistered compliance validator: {validator_id}")


def add_compliance_standard(self, standard: str):
    """Add a compliance standard to check."""
    self._compliance_standards.add(standard)


def remove_compliance_standard(self, standard: str):
    """Remove a compliance standard."""
    self._compliance_standards.discard(standard)


def get_registered_validators(self) -> List[str]:
    """Get list of registered validator IDs."""
    return list(self._validators.keys())


def get_compliance_standards(self) -> List[str]:
    """Get list of compliance standards being checked."""
    return list(self._compliance_standards)
