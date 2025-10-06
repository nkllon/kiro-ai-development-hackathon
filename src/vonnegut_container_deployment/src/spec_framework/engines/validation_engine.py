"""
Validation Engine - Systematic validation of specification completeness and quality.

Provides comprehensive validation including security, performance, and compliance checks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import (
    Specification,
    ValidationResults,
    Requirement,
    RequirementStatus,
    SpecificationStatus
)


logger = logging.getLogger(__name__)


class ValidationEngine(ReflectiveModule):
    """
    Systematic validation of specification completeness and quality.
    
    Provides multi-layered validation including structural, content, traceability,
    security, performance, and compliance validation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validation engine."""
        super().__init__()
        self._config = config or {}
        self._validation_rules = self._initialize_validation_rules()
        
        logger.info("ValidationEngine initialized with systematic validation")
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules based on systematic standards."""
        return {
            'structural_rules': {
                'min_requirements': 1,
                'required_user_story_fields': ['role', 'feature', 'benefit'],
                'min_acceptance_criteria': 1,
                'required_design_sections': ['overview', 'architecture', 'components']
            },
            'content_rules': {
                'ears_format_required': True,
                'testable_criteria_required': True,
                'business_value_required': True,
                'traceability_required': True
            },
            'security_rules': {
                'security_implications_required': False,  # Optional but recommended
                'threat_analysis_required': False,
                'compliance_mapping_required': False
            },
            'performance_rules': {
                'performance_implications_required': False,  # Optional but recommended
                'scalability_analysis_required': False,
                'performance_targets_required': False
            },
            'compliance_rules': {
                'audit_trail_required': True,
                'compliance_tags_required': False,
                'regulatory_mapping_required': False
            }
        }
    
    def validate_specification(self, specification: Specification) -> ValidationResults:
        """
        Perform comprehensive validation of specification.
        
        Args:
            specification: Specification to validate
            
        Returns:
            Complete validation results
        """
        validation = ValidationResults()
        
        # Structural validation
        validation.structural_validation = self._validate_structure(specification)
        
        # Content validation
        validation.content_validation = self._validate_content(specification)
        
        # Traceability validation
        validation.traceability_validation = self._validate_traceability(specification)
        
        # Security validation
        validation.security_validation = self._validate_security(specification)
        
        # Performance validation
        validation.performance_validation = self._validate_performance(specification)
        
        # Compliance validation
        validation.compliance_validation = self._validate_compliance(specification)
        
        # Calculate overall score
        validation.overall_score = self._calculate_overall_score(validation)
        
        # Collect errors and warnings
        validation.validation_errors = self._collect_validation_errors(validation)
        validation.validation_warnings = self._collect_validation_warnings(validation)
        
        validation.validated_at = datetime.now()
        
        logger.info(f"Validated specification {specification.name} - Score: {validation.overall_score:.1f}%")
        return validation
    
    def _validate_structure(self, specification: Specification) -> Dict[str, bool]:
        """Validate structural completeness of specification."""
        structural_validation = {}
        rules = self._validation_rules['structural_rules']
        
        # Check minimum requirements
        structural_validation['has_minimum_requirements'] = (
            len(specification.requirements) >= rules['min_requirements']
        )
        
        # Check user story completeness
        structural_validation['all_requirements_have_user_stories'] = all(
            all(getattr(req.user_story, field, None) for field in rules['required_user_story_fields'])
            for req in specification.requirements
        )
        
        # Check acceptance criteria
        structural_validation['all_requirements_have_acceptance_criteria'] = all(
            len(req.acceptance_criteria) >= rules['min_acceptance_criteria']
            for req in specification.requirements
        )
        
        # Check design structure (if design phase)
        if specification.status in [SpecificationStatus.DESIGN_COMPLETE, SpecificationStatus.TASKS_COMPLETE]:
            if specification.design:
                structural_validation['design_has_required_sections'] = all(
                    getattr(specification.design, section, None)
                    for section in rules['required_design_sections']
                )
            else:
                structural_validation['design_has_required_sections'] = False
        
        return structural_validation
    
    def _validate_content(self, specification: Specification) -> Dict[str, bool]:
        """Validate content quality of specification."""
        content_validation = {}
        rules = self._validation_rules['content_rules']
        
        # Check EARS format
        if rules['ears_format_required']:
            content_validation['all_criteria_use_ears_format'] = all(
                all(
                    ac.ears_format.condition and ac.ears_format.system and ac.ears_format.response
                    for ac in req.acceptance_criteria
                )
                for req in specification.requirements
            )
        
        # Check testability
        if rules['testable_criteria_required']:
            content_validation['all_criteria_are_testable'] = all(
                all(ac.testable for ac in req.acceptance_criteria)
                for req in specification.requirements
            )
        
        # Check business value
        if rules['business_value_required']:
            content_validation['all_requirements_have_business_value'] = all(
                bool(req.business_value) for req in specification.requirements
            )
        
        # Check requirement completeness
        content_validation['all_requirements_are_complete'] = all(
            req.is_complete() for req in specification.requirements
        )
        
        return content_validation
    
    def _validate_traceability(self, specification: Specification) -> Dict[str, bool]:
        """Validate traceability completeness."""
        traceability_validation = {}
        
        # Check if traceability matrix exists
        traceability_validation['has_traceability_matrix'] = (
            specification.traceability_matrix is not None
        )
        
        # Check requirement coverage
        if specification.traceability_matrix:
            coverage = specification.traceability_matrix.get_requirement_coverage()
            traceability_validation['requirement_coverage_complete'] = coverage >= 100.0
        else:
            traceability_validation['requirement_coverage_complete'] = False
        
        # Check for orphaned requirements
        orphaned_requirements = []
        for req in specification.requirements:
            if (specification.traceability_matrix and 
                req.id not in specification.traceability_matrix.requirement_to_design):
                orphaned_requirements.append(req.id)
        
        traceability_validation['no_orphaned_requirements'] = len(orphaned_requirements) == 0
        
        return traceability_validation
    
    def _validate_security(self, specification: Specification) -> Dict[str, bool]:
        """Validate security considerations."""
        security_validation = {}
        rules = self._validation_rules['security_rules']
        
        # Check security implications
        if rules['security_implications_required']:
            security_validation['all_requirements_have_security_implications'] = all(
                len(req.security_implications) > 0 for req in specification.requirements
            )
        else:
            # Optional - just check if any exist
            security_validation['has_security_considerations'] = any(
                len(req.security_implications) > 0 for req in specification.requirements
            )
        
        # Check security requirements
        security_validation['has_security_requirements'] = len(specification.security_requirements) > 0
        
        # Check threat analysis
        if rules['threat_analysis_required']:
            security_validation['has_threat_analysis'] = any(
                any(impl.threat_category for impl in req.security_implications)
                for req in specification.requirements
            )
        
        return security_validation
    
    def _validate_performance(self, specification: Specification) -> Dict[str, bool]:
        """Validate performance considerations."""
        performance_validation = {}
        rules = self._validation_rules['performance_rules']
        
        # Check performance implications
        if rules['performance_implications_required']:
            performance_validation['all_requirements_have_performance_implications'] = all(
                len(req.performance_implications) > 0 for req in specification.requirements
            )
        else:
            # Optional - just check if any exist
            performance_validation['has_performance_considerations'] = any(
                len(req.performance_implications) > 0 for req in specification.requirements
            )
        
        # Check performance requirements
        performance_validation['has_performance_requirements'] = len(specification.performance_requirements) > 0
        
        # Check scalability analysis
        if rules['scalability_analysis_required']:
            performance_validation['has_scalability_analysis'] = any(
                impl.target_values for impl in specification.performance_requirements
            )
        
        return performance_validation
    
    def _validate_compliance(self, specification: Specification) -> Dict[str, bool]:
        """Validate compliance considerations."""
        compliance_validation = {}
        rules = self._validation_rules['compliance_rules']
        
        # Check audit trail
        if rules['audit_trail_required']:
            compliance_validation['has_audit_trail'] = (
                specification.audit_trail is not None and
                len(specification.audit_trail.changes) > 0
            )
        
        # Check compliance tags
        if rules['compliance_tags_required']:
            compliance_validation['all_requirements_have_compliance_tags'] = all(
                len(req.compliance_tags) > 0 for req in specification.requirements
            )
        else:
            # Optional - just check if any exist
            compliance_validation['has_compliance_considerations'] = any(
                len(req.compliance_tags) > 0 for req in specification.requirements
            )
        
        # Check compliance metadata
        compliance_validation['has_compliance_metadata'] = (
            specification.compliance_metadata is not None and
            len(specification.compliance_metadata.regulatory_frameworks) > 0
        )
        
        return compliance_validation
    
    def _calculate_overall_score(self, validation: ValidationResults) -> float:
        """Calculate overall validation score."""
        all_validations = []
        
        # Collect all validation results
        all_validations.extend(validation.structural_validation.values())
        all_validations.extend(validation.content_validation.values())
        all_validations.extend(validation.traceability_validation.values())
        all_validations.extend(validation.security_validation.values())
        all_validations.extend(validation.performance_validation.values())
        all_validations.extend(validation.compliance_validation.values())
        
        if not all_validations:
            return 0.0
        
        # Calculate percentage of passed validations
        passed_validations = sum(1 for result in all_validations if result)
        return (passed_validations / len(all_validations)) * 100.0
    
    def _collect_validation_errors(self, validation: ValidationResults) -> List[str]:
        """Collect validation errors from results."""
        errors = []
        
        # Structural errors
        if not validation.structural_validation.get('has_minimum_requirements', True):
            errors.append("Specification must have at least one requirement")
        
        if not validation.structural_validation.get('all_requirements_have_user_stories', True):
            errors.append("All requirements must have complete user stories (role, feature, benefit)")
        
        if not validation.structural_validation.get('all_requirements_have_acceptance_criteria', True):
            errors.append("All requirements must have at least one acceptance criterion")
        
        # Content errors
        if not validation.content_validation.get('all_criteria_use_ears_format', True):
            errors.append("All acceptance criteria must use proper EARS format")
        
        if not validation.content_validation.get('all_criteria_are_testable', True):
            errors.append("All acceptance criteria must be testable")
        
        # Traceability errors
        if not validation.traceability_validation.get('requirement_coverage_complete', True):
            errors.append("All requirements must have traceability to design components")
        
        return errors
    
    def _collect_validation_warnings(self, validation: ValidationResults) -> List[str]:
        """Collect validation warnings from results."""
        warnings = []
        
        # Security warnings
        if not validation.security_validation.get('has_security_considerations', False):
            warnings.append("Consider adding security implications to requirements")
        
        # Performance warnings
        if not validation.performance_validation.get('has_performance_considerations', False):
            warnings.append("Consider adding performance implications to requirements")
        
        # Compliance warnings
        if not validation.compliance_validation.get('has_compliance_considerations', False):
            warnings.append("Consider adding compliance tags if regulatory requirements apply")
        
        return warnings
    
    def validate_requirement_quality(self, requirement: Requirement) -> Dict[str, bool]:
        """
        Validate individual requirement quality.
        
        Args:
            requirement: Requirement to validate
            
        Returns:
            Validation results for the requirement
        """
        validation = {}
        
        # User story validation
        user_story = requirement.user_story
        validation['has_complete_user_story'] = bool(
            user_story.role and user_story.feature and user_story.benefit
        )
        
        # Acceptance criteria validation
        validation['has_acceptance_criteria'] = len(requirement.acceptance_criteria) > 0
        validation['all_criteria_testable'] = all(
            ac.testable for ac in requirement.acceptance_criteria
        )
        validation['all_criteria_have_ears'] = all(
            ac.ears_format.condition and ac.ears_format.system and ac.ears_format.response
            for ac in requirement.acceptance_criteria
        )
        
        # Business value validation
        validation['has_business_value'] = bool(requirement.business_value)
        
        # Overall quality
        validation['is_high_quality'] = all(validation.values())
        
        return validation
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the validation engine."""
        return {
            "status": "healthy",
            "validation_rules_loaded": len(self._validation_rules),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if validation engine is ready for operation."""
        return len(self._validation_rules) > 0
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "validation_rules_count": float(len(self._validation_rules))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"