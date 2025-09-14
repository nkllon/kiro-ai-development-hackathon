"""
Beast Readiness Validator Core Core Validation

This module was extracted from beast_readiness_validator_core_core.py
as part of RM-DDD compliance refactoring.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import BacklogItem, Requirement, AcceptanceCriterion, DependencyReference
from .enums import BeastReadinessStatus, ApprovalStatus
from src.rm_ddd.core.health import ModuleHealth


def validate_beast_readiness(self, item: BacklogItem) -> ReadinessValidation:
    """
        Perform comprehensive beast-readiness validation.
        
        Args:
            item: BacklogItem to validate
            
        Returns:
            ReadinessValidation with detailed results and remediation guidance
        """
    try:
        validation_id = f'validation_{item.item_id}_{int(datetime.now().timestamp())}'
        completeness_report = self.check_completeness_criteria(item)
        dependency_statuses = self.verify_dependency_satisfaction(item)
        overall_ready = self._calculate_overall_readiness(completeness_report, dependency_statuses)
        confidence = self._calculate_confidence_score(completeness_report, dependency_statuses)
        next_actions = self._generate_next_actions(completeness_report, dependency_statuses, overall_ready)
        validation = ReadinessValidation(item_id=item.item_id, validation_id=validation_id, completeness_report=completeness_report, dependency_statuses=dependency_statuses, overall_beast_ready=overall_ready, confidence_score=confidence, validation_timestamp=datetime.now(), validator_id=self.module_name, next_actions=next_actions)
        self._validation_cache[item.item_id] = validation
        self._update_health_indicator('validation_success', HealthStatus.HEALTHY, True, f'Successfully validated item {item.item_id}')
        return validation
    except Exception as e:
        self.logger.error(f'Beast readiness validation failed for {item.item_id}: {str(e)}')
        self._update_health_indicator('validation_error', HealthStatus.UNHEALTHY, str(e), f'Validation failed for item {item.item_id}')
        raise

def check_completeness_criteria(self, item: BacklogItem) -> CompletenessReport:
    """
        Check completeness criteria for beast-readiness.
        
        Validates:
        - Requirements completeness and clarity
        - Acceptance criteria testability
        - Context and documentation adequacy
        - Ambiguity detection
        """
    criteria_results = []
    missing_elements = []
    remediation_actions = []
    req_criterion = self._validate_requirements_completeness(item.requirements)
    criteria_results.append(req_criterion)
    if not req_criterion.passed:
        missing_elements.extend(req_criterion.details.get('missing', []))
        remediation_actions.append(req_criterion.remediation_guidance)
    ac_criterion = self._validate_acceptance_criteria(item.acceptance_criteria)
    criteria_results.append(ac_criterion)
    if not ac_criterion.passed:
        missing_elements.extend(ac_criterion.details.get('missing', []))
        remediation_actions.append(ac_criterion.remediation_guidance)
    context_criterion = self._validate_context_adequacy(item)
    criteria_results.append(context_criterion)
    if not context_criterion.passed:
        missing_elements.extend(context_criterion.details.get('missing', []))
        remediation_actions.append(context_criterion.remediation_guidance)
    ambiguity_criterion = self._validate_ambiguity_absence(item)
    criteria_results.append(ambiguity_criterion)
    if not ambiguity_criterion.passed:
        missing_elements.extend(ambiguity_criterion.details.get('ambiguous', []))
        remediation_actions.append(ambiguity_criterion.remediation_guidance)
    total_weight = sum((c.weight for c in criteria_results))
    weighted_score = sum((c.score * c.weight for c in criteria_results))
    overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
    beast_ready = overall_score >= self._beast_readiness_threshold
    return CompletenessReport(overall_score=overall_score, criteria_results=criteria_results, missing_elements=missing_elements, remediation_actions=remediation_actions, beast_ready=beast_ready, validation_timestamp=datetime.now())

def verify_dependency_satisfaction(self, item: BacklogItem) -> List[DependencyStatus]:
    """
        Verify that all dependencies are satisfied or explicitly documented.
        
        Args:
            item: BacklogItem to check dependencies for
            
        Returns:
            List of DependencyStatus for each dependency
        """
    dependency_statuses = []
    for dep_ref in item.dependencies:
        status = self._check_dependency_satisfaction(dep_ref, item)
        dependency_statuses.append(status)
    return dependency_statuses

def _validate_requirements_completeness(self, requirements: List[Requirement]) -> ValidationCriterion:
    """Validate that requirements are complete and well-defined"""
    missing = []
    score = 1.0
    if not requirements:
        missing.append('No requirements defined')
        score = 0.0
    else:
        for req in requirements:
            if not req.description or len(req.description.strip()) < 10:
                missing.append(f'Requirement {req.requirement_id} has insufficient description')
                score -= 0.2
            if not req.acceptance_criteria:
                missing.append(f'Requirement {req.requirement_id} lacks acceptance criteria')
                score -= 0.3
    score = max(0.0, score)
    passed = score >= 0.8 and (not missing)
    return ValidationCriterion(criterion_name='requirements_completeness', description='Requirements are complete, clear, and well-defined', weight=0.3, passed=passed, score=score, remediation_guidance='Add detailed descriptions and acceptance criteria for all requirements', details={'missing': missing, 'requirement_count': len(requirements)})

def _validate_acceptance_criteria(self, criteria: List[AcceptanceCriterion]) -> ValidationCriterion:
    """Validate that acceptance criteria are testable and measurable"""
    missing = []
    score = 1.0
    if not criteria:
        missing.append('No acceptance criteria defined')
        score = 0.0
    else:
        for criterion in criteria:
            if not criterion.testable:
                missing.append(f'Criterion {criterion.criterion_id} is not testable')
                score -= 0.3
            if not criterion.measurable:
                missing.append(f'Criterion {criterion.criterion_id} is not measurable')
                score -= 0.3
            if not criterion.description or len(criterion.description.strip()) < 10:
                missing.append(f'Criterion {criterion.criterion_id} has insufficient description')
                score -= 0.2
    score = max(0.0, score)
    passed = score >= 0.8 and (not missing)
    return ValidationCriterion(criterion_name='acceptance_criteria_quality', description='Acceptance criteria are testable, measurable, and unambiguous', weight=0.3, passed=passed, score=score, remediation_guidance='Ensure all acceptance criteria are testable and measurable with clear descriptions', details={'missing': missing, 'criteria_count': len(criteria)})

def _validate_context_adequacy(self, item: BacklogItem) -> ValidationCriterion:
    """Validate that item has adequate context for independent execution"""
    missing = []
    score = 1.0
    if not item.title or len(item.title.strip()) < 5:
        missing.append('Title is too short or missing')
        score -= 0.2
    if not item.mpm_validation:
        missing.append('MPM validation is missing')
        score -= 0.4
    elif item.mpm_validation.approval_status != ApprovalStatus.APPROVED:
        missing.append('MPM validation is not approved')
        score -= 0.3
    if not item.track:
        missing.append('Strategic track not assigned')
        score -= 0.2
    score = max(0.0, score)
    passed = score >= 0.8 and (not missing)
    return ValidationCriterion(criterion_name='context_adequacy', description='Item has adequate context and supporting information', weight=0.2, passed=passed, score=score, remediation_guidance='Ensure item has clear title, approved MPM validation, and strategic track assignment', details={'missing': missing})

def _validate_ambiguity_absence(self, item: BacklogItem) -> ValidationCriterion:
    """Validate that item contains no ambiguous or interpretable elements"""
    ambiguous = []
    score = 1.0
    ambiguous_words = ['maybe', 'probably', 'should', 'could', 'might', 'perhaps', 'possibly']
    title_lower = item.title.lower()
    for word in ambiguous_words:
        if word in title_lower:
            ambiguous.append(f"Ambiguous word '{word}' in title")
            score -= 0.1
    for req in item.requirements:
        desc_lower = req.description.lower()
        for word in ambiguous_words:
            if word in desc_lower:
                ambiguous.append(f"Ambiguous word '{word}' in requirement {req.requirement_id}")
                score -= 0.1
    for criterion in item.acceptance_criteria:
        desc_lower = criterion.description.lower()
        for word in ambiguous_words:
            if word in desc_lower:
                ambiguous.append(f"Ambiguous word '{word}' in acceptance criterion {criterion.criterion_id}")
                score -= 0.1
    score = max(0.0, score)
    passed = score >= 0.9 and (not ambiguous)
    return ValidationCriterion(criterion_name='ambiguity_absence', description='Item contains no ambiguous or interpretable language', weight=0.2, passed=passed, score=score, remediation_guidance='Remove ambiguous language and replace with specific, measurable terms', details={'ambiguous': ambiguous})

def _check_dependency_satisfaction(self, dep_ref: DependencyReference, item: BacklogItem) -> DependencyStatus:
    """Check if a specific dependency is satisfied"""
    satisfied = bool(dep_ref.description and len(dep_ref.description.strip()) > 10)
    blocking_issues = []
    if not satisfied:
        blocking_issues.append('Dependency description is insufficient')
    evidence = dep_ref.description if satisfied else 'No clear satisfaction criteria'
    return DependencyStatus(dependency_id=dep_ref.dependency_id, target_item_id=dep_ref.target_item_id, satisfied=satisfied, satisfaction_evidence=evidence, blocking_issues=blocking_issues, estimated_resolution=None)
