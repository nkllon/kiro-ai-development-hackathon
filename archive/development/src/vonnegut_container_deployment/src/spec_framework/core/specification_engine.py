"""
Specification Engine - Central orchestrator for systematic specification workflow.

This is the core component that manages the Requirements → Design → Tasks → Implementation
workflow and enforces systematic progression through specification phases.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .base import ReflectiveModule
from .models import (
    Specification,
    SpecificationStatus,
    Requirement,
    RequirementStatus,
    ValidationResults,
    SpecificationChange,
    SpecificationDependency,
    DependencyType,
    CrossSpecImpactAnalysis,
    ImpactSeverity
)


logger = logging.getLogger(__name__)


class SpecificationEngine(ReflectiveModule):
    """
    Central orchestrator for the systematic specification workflow.
    
    Manages the complete lifecycle from requirements through implementation,
    enforcing systematic progression and maintaining traceability.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the specification engine."""
        super().__init__()
        self._config = config or {}
        self._specifications: Dict[str, Specification] = {}
        self._templates: Dict[str, Any] = {}
        self._governance_integration_enabled = self._config.get('governance_integration', True)
        
        # Initialize systematic templates based on RM-DDD patterns
        self._initialize_templates()
        
        logger.info("SpecificationEngine initialized with systematic workflow management")
    
    def _initialize_templates(self) -> None:
        """Initialize systematic templates based on RM-DDD reference patterns."""
        self._templates = {
            'user_story': {
                'format': 'As a {role}, I want {feature}, so that {benefit}',
                'validation_rules': [
                    'role_must_be_specific',
                    'feature_must_be_actionable',
                    'benefit_must_be_measurable'
                ]
            },
            'ears_format': {
                'format': '{trigger} {condition} THEN {system} SHALL {response}',
                'triggers': ['WHEN', 'IF', 'WHILE'],
                'validation_rules': [
                    'condition_must_be_observable',
                    'system_must_be_identifiable',
                    'response_must_be_testable'
                ]
            },
            'requirement_structure': {
                'required_fields': ['user_story', 'acceptance_criteria', 'business_value'],
                'minimum_acceptance_criteria': 1,
                'validation_rules': [
                    'all_criteria_must_be_testable',
                    'business_value_must_be_quantifiable'
                ]
            }
        }
    
    def create_specification(
        self,
        name: str,
        description: str = "",
        created_by: str = ""
    ) -> Specification:
        """
        Create a new specification with systematic structure.
        
        Args:
            name: Name of the specification
            description: Description of the specification
            created_by: Creator of the specification
            
        Returns:
            New specification instance
        """
        spec = Specification(
            name=name,
            description=description,
            created_by=created_by,
            status=SpecificationStatus.DRAFT
        )
        
        self._specifications[spec.id] = spec
        
        # Add creation to audit trail
        change = SpecificationChange(
            specification_id=spec.id,
            change_type="specification_created",
            description=f"Created specification: {name}",
            changed_by=created_by,
            changed_at=datetime.now()
        )
        spec.audit_trail.add_change(change)
        
        logger.info(f"Created new specification: {name} (ID: {spec.id})")
        return spec
    
    def get_specification(self, spec_id: str) -> Optional[Specification]:
        """Get a specification by ID."""
        return self._specifications.get(spec_id)
    
    def list_specifications(self) -> List[Specification]:
        """List all specifications."""
        return list(self._specifications.values())
    
    def add_requirement_to_specification(
        self,
        spec_id: str,
        requirement: Requirement
    ) -> bool:
        """
        Add a requirement to a specification with systematic validation.
        
        Args:
            spec_id: Specification ID
            requirement: Requirement to add
            
        Returns:
            True if requirement was added successfully
        """
        spec = self.get_specification(spec_id)
        if not spec:
            logger.error(f"Specification not found: {spec_id}")
            return False
        
        # Validate requirement structure
        if not self._validate_requirement_structure(requirement):
            logger.error(f"Requirement validation failed for spec {spec_id}")
            return False
        
        # Add requirement
        spec.add_requirement(requirement)
        
        # Update traceability matrix
        self._update_traceability_for_requirement(spec, requirement)
        
        logger.info(f"Added requirement {requirement.id} to specification {spec_id}")
        return True
    
    def _validate_requirement_structure(self, requirement: Requirement) -> bool:
        """
        Validate requirement structure against systematic templates.
        
        Args:
            requirement: Requirement to validate
            
        Returns:
            True if requirement structure is valid
        """
        # Check user story format
        user_story = requirement.user_story
        if not (user_story.role and user_story.feature and user_story.benefit):
            return False
        
        # Check acceptance criteria
        if len(requirement.acceptance_criteria) == 0:
            return False
        
        # Validate EARS format for acceptance criteria
        for criterion in requirement.acceptance_criteria:
            ears = criterion.ears_format
            if not (ears.condition and ears.system and ears.response):
                return False
        
        # Check testability
        if not all(ac.testable for ac in requirement.acceptance_criteria):
            return False
        
        return True
    
    def _update_traceability_for_requirement(
        self,
        spec: Specification,
        requirement: Requirement
    ) -> None:
        """Update traceability matrix for new requirement."""
        # This will be expanded when design and task components are added
        # For now, just ensure the requirement is tracked
        pass
    
    def validate_specification_phase_readiness(
        self,
        spec_id: str,
        target_phase: SpecificationStatus
    ) -> ValidationResults:
        """
        Validate if specification is ready to progress to target phase.
        
        Args:
            spec_id: Specification ID
            target_phase: Target phase to validate readiness for
            
        Returns:
            Validation results
        """
        spec = self.get_specification(spec_id)
        if not spec:
            return ValidationResults(
                validation_errors=["Specification not found"],
                overall_score=0.0
            )
        
        validation = ValidationResults()
        
        if target_phase == SpecificationStatus.DESIGN_COMPLETE:
            validation = self._validate_requirements_completeness(spec)
        elif target_phase == SpecificationStatus.TASKS_COMPLETE:
            validation = self._validate_design_completeness(spec)
        elif target_phase == SpecificationStatus.IMPLEMENTATION_IN_PROGRESS:
            validation = self._validate_tasks_completeness(spec)
        
        return validation
    
    def _validate_requirements_completeness(self, spec: Specification) -> ValidationResults:
        """Validate requirements phase completeness."""
        validation = ValidationResults()
        
        # Structural validation
        validation.structural_validation['has_requirements'] = len(spec.requirements) > 0
        validation.structural_validation['requirements_have_user_stories'] = all(
            req.user_story.role and req.user_story.feature and req.user_story.benefit
            for req in spec.requirements
        )
        validation.structural_validation['requirements_have_acceptance_criteria'] = all(
            len(req.acceptance_criteria) > 0 for req in spec.requirements
        )
        
        # Content validation
        validation.content_validation['all_criteria_testable'] = all(
            all(ac.testable for ac in req.acceptance_criteria)
            for req in spec.requirements
        )
        validation.content_validation['all_requirements_complete'] = all(
            req.is_complete() for req in spec.requirements
        )
        
        # Calculate overall score
        all_checks = []
        all_checks.extend(validation.structural_validation.values())
        all_checks.extend(validation.content_validation.values())
        
        validation.overall_score = (sum(all_checks) / len(all_checks)) * 100.0 if all_checks else 0.0
        
        # Add errors for failed validations
        if not validation.structural_validation.get('has_requirements', False):
            validation.validation_errors.append("Specification must have at least one requirement")
        
        if not validation.content_validation.get('all_requirements_complete', False):
            validation.validation_errors.append("All requirements must be complete with user stories and testable acceptance criteria")
        
        return validation
    
    def _validate_design_completeness(self, spec: Specification) -> ValidationResults:
        """Validate design phase completeness."""
        validation = ValidationResults()
        
        # Structural validation
        validation.structural_validation['has_design'] = spec.design is not None
        
        if spec.design:
            validation.structural_validation['design_has_overview'] = bool(spec.design.overview)
            validation.structural_validation['design_has_architecture'] = bool(spec.design.architecture)
            validation.structural_validation['design_has_components'] = len(spec.design.components) > 0
        
        # Traceability validation
        coverage = spec.traceability_matrix.get_requirement_coverage()
        validation.traceability_validation['requirement_coverage'] = coverage >= 100.0
        
        # Calculate overall score
        all_checks = []
        all_checks.extend(validation.structural_validation.values())
        all_checks.extend(validation.traceability_validation.values())
        
        validation.overall_score = (sum(all_checks) / len(all_checks)) * 100.0 if all_checks else 0.0
        
        return validation
    
    def _validate_tasks_completeness(self, spec: Specification) -> ValidationResults:
        """Validate tasks phase completeness."""
        validation = ValidationResults()
        
        # Structural validation
        validation.structural_validation['has_tasks'] = len(spec.tasks) > 0
        validation.structural_validation['tasks_reference_requirements'] = all(
            len(task.requirements_references) > 0 for task in spec.tasks
        )
        
        # Calculate overall score
        all_checks = list(validation.structural_validation.values())
        validation.overall_score = (sum(all_checks) / len(all_checks)) * 100.0 if all_checks else 0.0
        
        return validation
    
    def progress_specification_phase(
        self,
        spec_id: str,
        target_phase: SpecificationStatus,
        validated_by: str = ""
    ) -> bool:
        """
        Progress specification to next phase with systematic validation.
        
        Args:
            spec_id: Specification ID
            target_phase: Target phase to progress to
            validated_by: Person validating the progression
            
        Returns:
            True if progression was successful
        """
        spec = self.get_specification(spec_id)
        if not spec:
            logger.error(f"Specification not found: {spec_id}")
            return False
        
        # Validate readiness for target phase
        validation = self.validate_specification_phase_readiness(spec_id, target_phase)
        
        if not validation.is_valid():
            logger.error(f"Specification {spec_id} not ready for phase {target_phase.value}")
            logger.error(f"Validation errors: {validation.validation_errors}")
            return False
        
        # Update specification status
        old_status = spec.status
        spec.status = target_phase
        spec.updated_at = datetime.now()
        spec.validation_results = validation
        
        # Add to audit trail
        change = SpecificationChange(
            specification_id=spec_id,
            change_type="phase_progression",
            description=f"Progressed from {old_status.value} to {target_phase.value}",
            changed_by=validated_by,
            changed_at=datetime.now()
        )
        spec.audit_trail.add_change(change)
        
        logger.info(f"Progressed specification {spec_id} to phase {target_phase.value}")
        return True
    
    def add_specification_dependency(
        self,
        dependent_spec_id: str,
        dependency_spec_id: str,
        dependency_type: DependencyType,
        description: str = ""
    ) -> bool:
        """
        Add dependency between specifications.
        
        Args:
            dependent_spec_id: ID of specification that depends on another
            dependency_spec_id: ID of specification being depended upon
            dependency_type: Type of dependency
            description: Description of the dependency
            
        Returns:
            True if dependency was added successfully
        """
        dependent_spec = self.get_specification(dependent_spec_id)
        dependency_spec = self.get_specification(dependency_spec_id)
        
        if not dependent_spec or not dependency_spec:
            logger.error("One or both specifications not found for dependency")
            return False
        
        # Check for circular dependencies
        if self._would_create_circular_dependency(dependent_spec_id, dependency_spec_id):
            logger.error("Cannot add dependency - would create circular dependency")
            return False
        
        # Create dependency
        dependency = SpecificationDependency(
            dependent_spec=dependent_spec_id,
            dependency_spec=dependency_spec_id,
            dependency_type=dependency_type
        )
        
        dependent_spec.dependencies.append(dependency)
        
        # Add to audit trail
        change = SpecificationChange(
            specification_id=dependent_spec_id,
            change_type="dependency_added",
            description=f"Added {dependency_type.value} dependency on {dependency_spec.name}",
            changed_at=datetime.now()
        )
        dependent_spec.audit_trail.add_change(change)
        
        logger.info(f"Added dependency: {dependent_spec.name} {dependency_type.value} {dependency_spec.name}")
        return True
    
    def _would_create_circular_dependency(
        self,
        dependent_spec_id: str,
        dependency_spec_id: str
    ) -> bool:
        """Check if adding dependency would create circular dependency."""
        # Simple check - in production this would be more sophisticated
        dependency_spec = self.get_specification(dependency_spec_id)
        if not dependency_spec:
            return False
        
        # Check if dependency_spec already depends on dependent_spec
        for dep in dependency_spec.dependencies:
            if dep.dependency_spec == dependent_spec_id:
                return True
        
        return False
    
    def analyze_cross_spec_impact(
        self,
        change: SpecificationChange
    ) -> CrossSpecImpactAnalysis:
        """
        Analyze impact of specification change across dependent specifications.
        
        Args:
            change: Specification change to analyze
            
        Returns:
            Cross-specification impact analysis
        """
        analysis = CrossSpecImpactAnalysis(source_change=change)
        
        # Find all specifications that depend on the changed specification
        for spec in self._specifications.values():
            for dependency in spec.dependencies:
                if dependency.dependency_spec == change.specification_id:
                    analysis.impacted_specs.append(spec.id)
        
        # Determine impact severity based on change type and number of impacted specs
        if len(analysis.impacted_specs) == 0:
            analysis.impact_severity = ImpactSeverity.LOW
        elif len(analysis.impacted_specs) <= 2:
            analysis.impact_severity = ImpactSeverity.MEDIUM
        else:
            analysis.impact_severity = ImpactSeverity.HIGH
        
        # Add recommended actions based on impact
        if analysis.impact_severity in [ImpactSeverity.MEDIUM, ImpactSeverity.HIGH]:
            from .models import RecommendedAction, Priority
            analysis.recommended_actions.append(
                RecommendedAction(
                    action_type="review_dependencies",
                    description="Review and validate all dependent specifications",
                    priority=Priority.HIGH if analysis.impact_severity == ImpactSeverity.HIGH else Priority.MEDIUM
                )
            )
        
        return analysis
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the specification engine."""
        return {
            "status": "healthy",
            "specifications_count": len(self._specifications),
            "templates_loaded": len(self._templates),
            "governance_integration": self._governance_integration_enabled,
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if specification engine is ready for operation."""
        return len(self._templates) > 0
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        if not self._specifications:
            return {
                "specifications_total": 0.0,
                "requirements_total": 0.0,
                "average_completion": 0.0,
                "validation_success_rate": 0.0
            }
        
        total_requirements = sum(len(spec.requirements) for spec in self._specifications.values())
        total_completion = sum(spec.get_completion_percentage() for spec in self._specifications.values())
        avg_completion = total_completion / len(self._specifications)
        
        # Calculate validation success rate
        valid_specs = sum(1 for spec in self._specifications.values() if spec.validation_results.is_valid())
        validation_rate = (valid_specs / len(self._specifications)) * 100.0
        
        return {
            "specifications_total": float(len(self._specifications)),
            "requirements_total": float(total_requirements),
            "average_completion": avg_completion,
            "validation_success_rate": validation_rate
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        elif len(self._specifications) == 0:
            return "ready"
        else:
            return "active"