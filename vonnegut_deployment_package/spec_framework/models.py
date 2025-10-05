"""
Core data models for the Spec Framework.

This module defines the fundamental data structures for specification document
management, validation, and dependency governance.
"""

import os
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)


class WorkflowStage(Enum):
    """Enumeration of specification document workflow stages."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"
    COMPLETE = "complete"


class ApprovalStatus(Enum):
    """Enumeration of specification document approval statuses."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class DependencyType(Enum):
    """Enumeration of dependency relationship types."""
    FOUNDATION = "foundation"
    SERVICE = "service"
    INTEGRATION = "integration"
    OPTIONAL = "optional"


@dataclass
class SemanticVersion:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def increment_patch(self) -> "SemanticVersion":
        return SemanticVersion(self.major, self.minor, self.patch + 1)
    
    def increment_minor(self) -> "SemanticVersion":
        return SemanticVersion(self.major, self.minor + 1, 0)
    
    def increment_major(self) -> "SemanticVersion":
        return SemanticVersion(self.major + 1, 0, 0)


@dataclass
class ChangeSet:
    """Represents a set of changes to a specification document."""
    added_sections: List[str] = field(default_factory=list)
    modified_sections: List[str] = field(default_factory=list)
    removed_sections: List[str] = field(default_factory=list)
    metadata_changes: Dict[str, Any] = field(default_factory=dict)
    
    def has_changes(self) -> bool:
        """Check if this changeset contains any changes."""
        return bool(
            self.added_sections or 
            self.modified_sections or 
            self.removed_sections or 
            self.metadata_changes
        )


@dataclass
class AuditEntry:
    """Audit trail entry for specification document changes."""
    timestamp: datetime
    event_type: str
    user_id: str
    changes: ChangeSet
    correlation_id: str
    
    def __post_init__(self):
        if not self.correlation_id:
            import uuid
            self.correlation_id = str(uuid.uuid4())


@dataclass
class LifecycleEvent:
    """Lifecycle event for specification document management."""
    event_type: str
    spec_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationError:
    """Validation error with specific details."""
    error_type: str
    message: str
    location: Optional[str] = None
    severity: str = "error"


@dataclass
class ValidationWarning:
    """Validation warning with specific details."""
    warning_type: str
    message: str
    location: Optional[str] = None


@dataclass
class DocumentTemplate:
    """Template for document sections or complete documents."""
    name: str
    content: str
    description: str
    variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class RemediationGuide:
    """Guidance for fixing validation errors."""
    error_type: str
    specific_guidance: str
    examples: List[str] = field(default_factory=list)
    templates: List[DocumentTemplate] = field(default_factory=list)
    
    def generate_corrective_actions(self) -> List[str]:
        """Generate list of corrective actions based on guidance."""
        actions = [self.specific_guidance]
        if self.examples:
            actions.append(f"See examples: {', '.join(self.examples[:3])}")
        if self.templates:
            actions.append(f"Use templates: {', '.join([t.name for t in self.templates[:3]])}")
        return actions


@dataclass
class ValidationResult:
    """Result of document validation with remediation guidance."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    remediation_guidance: Optional[RemediationGuide] = None
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    def has_blocking_errors(self) -> bool:
        """Check if validation result has errors that block progression."""
        return any(error.severity == "error" for error in self.errors)
    
    def generate_report(self) -> str:
        """Generate human-readable validation report."""
        report = []
        report.append(f"Validation Status: {'PASS' if self.is_valid else 'FAIL'}")
        report.append(f"Timestamp: {self.validation_timestamp}")
        
        if self.errors:
            report.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                location = f" at {error.location}" if error.location else ""
                report.append(f"  - {error.error_type}: {error.message}{location}")
        
        if self.warnings:
            report.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                location = f" at {warning.location}" if warning.location else ""
                report.append(f"  - {warning.warning_type}: {warning.message}{location}")
        
        if self.remediation_guidance:
            report.append(f"\nRemediation Guidance:")
            report.append(f"  {self.remediation_guidance.specific_guidance}")
            if self.remediation_guidance.examples:
                report.append(f"  Examples: {', '.join(self.remediation_guidance.examples)}")
        
        return "\n".join(report)


@dataclass
class Dependency:
    """Specification dependency relationship."""
    source_spec: str
    target_spec: str
    dependency_type: DependencyType
    
    def validate_dag_compliance(self, graph: "DependencyGraph") -> ValidationResult:
        """Validate this dependency doesn't create cycles in the graph."""
        # This will be implemented when DependencyGraph is complete
        return ValidationResult(is_valid=True)


@dataclass
class DependencyGraph:
    """Graph representation of specification dependencies."""
    nodes: List[str] = field(default_factory=list)  # spec names
    edges: List[Dependency] = field(default_factory=list)
    
    def is_acyclic(self) -> bool:
        """Check if the dependency graph is acyclic (DAG compliant)."""
        # Implement topological sort to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            # Get all dependencies of this node
            for edge in self.edges:
                if edge.source_spec == node:
                    neighbor = edge.target_spec
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if has_cycle(node):
                    return False
        
        return True
    
    def find_cycles(self) -> List[List[str]]:
        """Find all cycles in the dependency graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def find_cycle_from_node(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for edge in self.edges:
                if edge.source_spec == node:
                    neighbor = edge.target_spec
                    if neighbor not in visited:
                        find_cycle_from_node(neighbor)
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self.nodes:
            if node not in visited:
                find_cycle_from_node(node)
        
        return cycles
    
    def validate_service_interfaces(self) -> ValidationResult:
        """Validate that service interfaces are properly used."""
        # Placeholder implementation - will be enhanced in dependency manager
        return ValidationResult(is_valid=True)


@dataclass
class ImpactAnalysis:
    """Analysis of the impact of changes to a specification."""
    affected_specs: List[str] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    migration_required: bool = False
    risk_level: str = "low"  # low, medium, high, critical


@dataclass
class SpecificationDocument(ReflectiveModule):
    """Core specification document model with workflow and lifecycle management."""
    
    id: str
    name: str
    version: SemanticVersion
    requirements_path: str
    design_path: Optional[str] = None
    tasks_path: Optional[str] = None
    dependencies: List[Dependency] = field(default_factory=list)
    workflow_stage: WorkflowStage = WorkflowStage.REQUIREMENTS
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    audit_trail: List[AuditEntry] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize ReflectiveModule after dataclass initialization."""
        super().__init__()
    
    def validate_structure(self) -> ValidationResult:
        """Validate the structure of this specification document."""
        errors = []
        warnings = []
        
        # Check required paths exist
        if not os.path.exists(self.requirements_path):
            errors.append(ValidationError(
                error_type="missing_file",
                message=f"Requirements file not found: {self.requirements_path}",
                location=self.requirements_path
            ))
        
        # Check workflow progression
        if self.workflow_stage == WorkflowStage.DESIGN and not self.design_path:
            errors.append(ValidationError(
                error_type="workflow_violation",
                message="Design stage requires design_path to be set",
                location="design_path"
            ))
        
        if self.workflow_stage == WorkflowStage.TASKS and not self.tasks_path:
            errors.append(ValidationError(
                error_type="workflow_violation", 
                message="Tasks stage requires tasks_path to be set",
                location="tasks_path"
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def get_dependencies(self) -> List[Dependency]:
        """Get all dependencies for this specification."""
        return self.dependencies.copy()
    
    def can_progress_to_stage(self, target_stage: WorkflowStage) -> bool:
        """Check if this specification can progress to the target workflow stage."""
        stage_order = [
            WorkflowStage.REQUIREMENTS,
            WorkflowStage.DESIGN,
            WorkflowStage.TASKS,
            WorkflowStage.COMPLETE
        ]
        
        current_index = stage_order.index(self.workflow_stage)
        target_index = stage_order.index(target_stage)
        
        # Can only progress forward one stage at a time
        return target_index == current_index + 1
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            "module_id": f"spec_document_{self.id}",
            "name": self.name,
            "version": str(self.version),
            "workflow_stage": self.workflow_stage.value,
            "approval_status": self.approval_status.value,
            "dependencies_count": len(self.dependencies),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant."""
        capabilities = [ModuleCapability.VALIDATION]
        
        if self.workflow_stage in [WorkflowStage.TASKS, WorkflowStage.COMPLETE]:
            capabilities.append(ModuleCapability.CORE_FUNCTIONALITY)
        
        if self.dependencies:
            capabilities.append(ModuleCapability.API_INTEGRATION)
        
        return capabilities
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant."""
        validation_result = self.validate_structure()
        
        if validation_result.is_valid:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif validation_result.has_blocking_errors():
            status = ModuleStatus.ERROR
            health_score = 0.0
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
        
        issues = [error.message for error in validation_result.errors]
        issues.extend([warning.message for warning in validation_result.warnings])
        
        return ModuleHealth(
            module_id=f"spec_document_{self.id}",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self.created_at).total_seconds(),
            error_count=len(validation_result.errors),
            warning_count=len(validation_result.warnings)
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant."""
        validation_result = self.validate_structure()
        
        if validation_result.is_valid:
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=self.get_capabilities()
            )
        
        # Degrade capabilities based on validation issues
        degraded = []
        remaining = []
        
        for capability in self.get_capabilities():
            if capability == ModuleCapability.VALIDATION and validation_result.has_blocking_errors():
                degraded.append(capability)
            else:
                remaining.append(capability)
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded,
            remaining_capabilities=remaining,
            error_message=f"Validation issues: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings"
        )
    
    # Legacy methods for backward compatibility
    def health(self) -> Dict[str, Any]:
        """Return health status (legacy method)."""
        health_status = self.get_health_status()
        return {
            "status": health_status.status.value,
            "health_score": health_status.health_score,
            "workflow_stage": self.workflow_stage.value,
            "approval_status": self.approval_status.value,
            "validation_errors": health_status.error_count,
            "validation_warnings": health_status.warning_count,
            "dependencies_count": len(self.dependencies),
            "last_updated": self.updated_at.isoformat()
        }
    
    def ready(self) -> bool:
        """Check if this specification is ready for use."""
        health_status = self.get_health_status()
        return (
            health_status.status == ModuleStatus.HEALTHY and
            self.approval_status == ApprovalStatus.APPROVED and
            self.workflow_stage in [WorkflowStage.TASKS, WorkflowStage.COMPLETE]
        )
    
    def metrics(self) -> Dict[str, float]:
        """Return performance metrics for this specification."""
        health_status = self.get_health_status()
        return {
            "validation_score": health_status.health_score,
            "completion_percentage": self._calculate_completion_percentage(),
            "dependency_complexity": float(len(self.dependencies)),
            "audit_trail_length": float(len(self.audit_trail))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        health_status = self.get_health_status()
        if health_status.status == ModuleStatus.ERROR:
            return "invalid"
        elif self.approval_status == ApprovalStatus.DEPRECATED:
            return "deprecated"
        elif self.approval_status == ApprovalStatus.APPROVED:
            return "approved"
        elif self.approval_status == ApprovalStatus.UNDER_REVIEW:
            return "under_review"
        else:
            return "draft"
    
    def _calculate_completion_percentage(self) -> float:
        """Calculate completion percentage based on workflow stage."""
        stage_percentages = {
            WorkflowStage.REQUIREMENTS: 25.0,
            WorkflowStage.DESIGN: 50.0,
            WorkflowStage.TASKS: 75.0,
            WorkflowStage.COMPLETE: 100.0
        }
        return stage_percentages.get(self.workflow_stage, 0.0)