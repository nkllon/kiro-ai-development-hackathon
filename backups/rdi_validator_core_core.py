"""
Rdi Validator Core Core

This module was extracted from rdi_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RDIComplianceLevel(Enum):
    """RDI compliance levels"""

    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    COMPLIANT = "compliant"
    EXCELLENT = "excellent"


class RDIValidationType(Enum):
    """RDI validation types"""

    REQUIREMENTS_TRACEABILITY = "requirements_traceability"
    IMPLEMENTATION_QUALITY = "implementation_quality"
    SYSTEMATIC_APPROACH = "systematic_approach"
    PREVENTION_MEASURES = "prevention_measures"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"


@dataclass
class RDIValidationResult:
    """RDI validation result"""

    validation_id: str
    component_name: str
    validation_type: RDIValidationType
    compliance_level: RDIComplianceLevel
    score: float
    findings: List[str]
    recommendations: List[str]
    validation_timestamp: datetime
    validator: str


class RDIValidator:
    """
    RDI (Requirements-Driven Implementation) Validator

    Systematic validation engine for ensuring requirements-driven implementation
    and maintaining systematic development principles.
    """

    def __init__(self):
        """Initialize RDI validator"""
        self.validation_history: List[RDIValidationResult] = []
        self.compliance_standards: Dict[str, List[str]] = {}
        self.improvement_recommendations: List[str] = []
        self._initialize_compliance_standards()
        logger.info("RDI Validator initialized")

    def _initialize_compliance_standards(self):
        """Initialize RDI compliance standards"""
        self.compliance_standards = {
            "requirements_traceability": [
                "All features traceable to requirements",
                "Requirements documented and accessible",
                "Implementation matches requirements",
                "Changes tracked and validated",
            ],
            "implementation_quality": [
                "Code follows systematic principles",
                "Proper error handling implemented",
                "Comprehensive testing coverage",
                "Documentation is complete and accurate",
            ],
            "systematic_approach": [
                "Systematic development process followed",
                "Quality gates implemented",
                "Automated validation in place",
                "Continuous monitoring active",
            ],
            "prevention_measures": [
                "Prevention systems implemented",
                "Issue detection automated",
                "Learning systems in place",
                "Continuous improvement active",
            ],
            "continuous_improvement": [
                "Metrics collection implemented",
                "Feedback loops established",
                "Learning from failures",
                "Process optimization ongoing",
            ],
        }

    def validate_component(
        self,
        component_name: str,
        component_data: Dict[str, Any],
        validation_types: List[RDIValidationType] = None,
    ) -> List[RDIValidationResult]:
        """
        Validate a component for RDI compliance

        Args:
            component_name: Name of the component to validate
            component_data: Component data and metadata
            validation_types: Types of validation to perform

        Returns:
            List of validation results
        """
        if validation_types is None:
            validation_types = list(RDIValidationType)
        logger.info(f"Validating component {component_name} for RDI compliance")
        results = []
        for validation_type in validation_types:
            result = self._perform_validation(
                component_name, component_data, validation_type
            )
            results.append(result)
            self.validation_history.append(result)
        return results

    def _perform_validation(
        self,
        component_name: str,
        component_data: Dict[str, Any],
        validation_type: RDIValidationType,
    ) -> RDIValidationResult:
        """Perform specific validation type"""
        validation_id = f"rdi_{int(datetime.now().timestamp())}_{validation_type.value}"
        standards = self.compliance_standards.get(validation_type.value, [])
        findings = []
        recommendations = []
        score = 0.0
        if validation_type == RDIValidationType.REQUIREMENTS_TRACEABILITY:
            findings, recommendations, score = self._validate_requirements_traceability(
                component_data, standards
            )
        elif validation_type == RDIValidationType.IMPLEMENTATION_QUALITY:
            findings, recommendations, score = self._validate_implementation_quality(
                component_data, standards
            )
        elif validation_type == RDIValidationType.SYSTEMATIC_APPROACH:
            findings, recommendations, score = self._validate_systematic_approach(
                component_data, standards
            )
        elif validation_type == RDIValidationType.PREVENTION_MEASURES:
            findings, recommendations, score = self._validate_prevention_measures(
                component_data, standards
            )
        elif validation_type == RDIValidationType.CONTINUOUS_IMPROVEMENT:
            findings, recommendations, score = self._validate_continuous_improvement(
                component_data, standards
            )
        compliance_level = self._determine_compliance_level(score)
        return RDIValidationResult(
            validation_id=validation_id,
            component_name=component_name,
            validation_type=validation_type,
            compliance_level=compliance_level,
            score=score,
            findings=findings,
            recommendations=recommendations,
            validation_timestamp=datetime.now(),
            validator="RDI Validator",
        )

    def _validate_requirements_traceability(
        self, component_data: Dict[str, Any], standards: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Validate requirements traceability"""
        findings = []
        recommendations = []
        score = 0.0
        if component_data.get("requirements_documented", False):
            score += 0.25
            findings.append("✅ Requirements are documented")
        else:
            findings.append("❌ Requirements not documented")
            recommendations.append("Document all requirements clearly")
        if component_data.get("implementation_matches_requirements", False):
            score += 0.25
            findings.append("✅ Implementation matches requirements")
        else:
            findings.append("❌ Implementation may not match requirements")
            recommendations.append("Ensure implementation aligns with requirements")
        if component_data.get("changes_tracked", False):
            score += 0.25
            findings.append("✅ Changes are tracked")
        else:
            findings.append("❌ Changes not properly tracked")
            recommendations.append("Implement change tracking system")
        if component_data.get("validation_in_place", False):
            score += 0.25
            findings.append("✅ Validation system in place")
        else:
            findings.append("❌ Validation system missing")
            recommendations.append("Implement systematic validation")
        return (findings, recommendations, score)

    def _validate_implementation_quality(
        self, component_data: Dict[str, Any], standards: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Validate implementation quality"""
        findings = []
        recommendations = []
        score = 0.0
        if component_data.get("follows_systematic_principles", False):
            score += 0.25
            findings.append("✅ Follows systematic principles")
        else:
            findings.append("❌ May not follow systematic principles")
            recommendations.append("Implement systematic development approach")
        if component_data.get("error_handling_implemented", False):
            score += 0.25
            findings.append("✅ Error handling implemented")
        else:
            findings.append("❌ Error handling missing or insufficient")
            recommendations.append("Implement comprehensive error handling")
        test_coverage = component_data.get("test_coverage", 0.0)
        if test_coverage >= 0.8:
            score += 0.25
            findings.append(f"✅ Good test coverage ({test_coverage:.1%})")
        else:
            findings.append(f"❌ Insufficient test coverage ({test_coverage:.1%})")
            recommendations.append("Increase test coverage to at least 80%")
        if component_data.get("documentation_complete", False):
            score += 0.25
            findings.append("✅ Documentation is complete")
        else:
            findings.append("❌ Documentation incomplete")
            recommendations.append("Complete and maintain documentation")
        return (findings, recommendations, score)

    def _validate_systematic_approach(
        self, component_data: Dict[str, Any], standards: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Validate systematic approach"""
        findings = []
        recommendations = []
        score = 0.0
        if component_data.get("systematic_process_followed", False):
            score += 0.25
            findings.append("✅ Systematic process followed")
        else:
            findings.append("❌ Systematic process not followed")
            recommendations.append(
                "Implement and follow systematic development process"
            )
        if component_data.get("quality_gates_implemented", False):
            score += 0.25
            findings.append("✅ Quality gates implemented")
        else:
            findings.append("❌ Quality gates missing")
            recommendations.append("Implement automated quality gates")
        if component_data.get("automated_validation", False):
            score += 0.25
            findings.append("✅ Automated validation in place")
        else:
            findings.append("❌ Automated validation missing")
            recommendations.append("Implement automated validation systems")
        if component_data.get("continuous_monitoring", False):
            score += 0.25
            findings.append("✅ Continuous monitoring active")
        else:
            findings.append("❌ Continuous monitoring missing")
            recommendations.append("Implement continuous monitoring")
        return (findings, recommendations, score)

    def _validate_prevention_measures(
        self, component_data: Dict[str, Any], standards: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Validate prevention measures"""
        findings = []
        recommendations = []
        score = 0.0
        if component_data.get("prevention_systems_implemented", False):
            score += 0.25
            findings.append("✅ Prevention systems implemented")
        else:
            findings.append("❌ Prevention systems missing")
            recommendations.append("Implement systematic prevention architecture")
        if component_data.get("issue_detection_automated", False):
            score += 0.25
            findings.append("✅ Issue detection automated")
        else:
            findings.append("❌ Issue detection not automated")
            recommendations.append("Implement automated issue detection")
        if component_data.get("learning_systems_in_place", False):
            score += 0.25
            findings.append("✅ Learning systems in place")
        else:
            findings.append("❌ Learning systems missing")
            recommendations.append("Implement learning and improvement systems")
        if component_data.get("continuous_improvement_active", False):
            score += 0.25
            findings.append("✅ Continuous improvement active")
        else:
            findings.append("❌ Continuous improvement not active")
            recommendations.append("Implement continuous improvement processes")
        return (findings, recommendations, score)

    def _validate_continuous_improvement(
        self, component_data: Dict[str, Any], standards: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """Validate continuous improvement"""
        findings = []
        recommendations = []
        score = 0.0
        if component_data.get("metrics_collection_implemented", False):
            score += 0.25
            findings.append("✅ Metrics collection implemented")
        else:
            findings.append("❌ Metrics collection missing")
            recommendations.append("Implement comprehensive metrics collection")
        if component_data.get("feedback_loops_established", False):
            score += 0.25
            findings.append("✅ Feedback loops established")
        else:
            findings.append("❌ Feedback loops missing")
            recommendations.append("Establish feedback loops for continuous learning")
        if component_data.get("learning_from_failures", False):
            score += 0.25
            findings.append("✅ Learning from failures implemented")
        else:
            findings.append("❌ Learning from failures not implemented")
            recommendations.append("Implement systematic learning from failures")
        if component_data.get("process_optimization_ongoing", False):
            score += 0.25
            findings.append("✅ Process optimization ongoing")
        else:
            findings.append("❌ Process optimization not active")
            recommendations.append("Implement ongoing process optimization")
        return (findings, recommendations, score)

    def _determine_compliance_level(self, score: float) -> RDIComplianceLevel:
        """Determine compliance level based on score"""
        if score >= 0.9:
            return RDIComplianceLevel.EXCELLENT
        elif score >= 0.7:
            return RDIComplianceLevel.COMPLIANT
        elif score >= 0.5:
            return RDIComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return RDIComplianceLevel.NON_COMPLIANT

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get overall compliance summary"""
        if not self.validation_history:
            return {"message": "No validations performed yet"}
        total_validations = len(self.validation_history)
        excellent_count = sum(
            (
                1
                for v in self.validation_history
                if v.compliance_level == RDIComplianceLevel.EXCELLENT
            )
        )
        compliant_count = sum(
            (
                1
                for v in self.validation_history
                if v.compliance_level == RDIComplianceLevel.COMPLIANT
            )
        )
        partially_compliant_count = sum(
            (
                1
                for v in self.validation_history
                if v.compliance_level == RDIComplianceLevel.PARTIALLY_COMPLIANT
            )
        )
        non_compliant_count = sum(
            (
                1
                for v in self.validation_history
                if v.compliance_level == RDIComplianceLevel.NON_COMPLIANT
            )
        )
        average_score = (
            sum((v.score for v in self.validation_history)) / total_validations
        )
        return {
            "total_validations": total_validations,
            "excellent": excellent_count,
            "compliant": compliant_count,
            "partially_compliant": partially_compliant_count,
            "non_compliant": non_compliant_count,
            "average_score": average_score,
            "compliance_rate": (excellent_count + compliant_count) / total_validations,
        }

    def generate_improvement_plan(self) -> List[str]:
        """Generate improvement plan based on validation results"""
        plan = []
        all_recommendations = []
        for validation in self.validation_history:
            all_recommendations.extend(validation.recommendations)
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        sorted_recommendations = sorted(
            recommendation_counts.items(), key=lambda x: x[1], reverse=True
        )
        for rec, count in sorted_recommendations[:10]:
            plan.append(
                f"Priority {len(plan) + 1}: {rec} (appears in {count} validations)"
            )
        return plan


def __init__(self):
    """Initialize RDI validator"""
    self.validation_history: List[RDIValidationResult] = []
    self.compliance_standards: Dict[str, List[str]] = {}
    self.improvement_recommendations: List[str] = []
    self._initialize_compliance_standards()
    logger.info("RDI Validator initialized")


def _initialize_compliance_standards(self):
    """Initialize RDI compliance standards"""
    self.compliance_standards = {
        "requirements_traceability": [
            "All features traceable to requirements",
            "Requirements documented and accessible",
            "Implementation matches requirements",
            "Changes tracked and validated",
        ],
        "implementation_quality": [
            "Code follows systematic principles",
            "Proper error handling implemented",
            "Comprehensive testing coverage",
            "Documentation is complete and accurate",
        ],
        "systematic_approach": [
            "Systematic development process followed",
            "Quality gates implemented",
            "Automated validation in place",
            "Continuous monitoring active",
        ],
        "prevention_measures": [
            "Prevention systems implemented",
            "Issue detection automated",
            "Learning systems in place",
            "Continuous improvement active",
        ],
        "continuous_improvement": [
            "Metrics collection implemented",
            "Feedback loops established",
            "Learning from failures",
            "Process optimization ongoing",
        ],
    }


def _perform_validation(
    self,
    component_name: str,
    component_data: Dict[str, Any],
    validation_type: RDIValidationType,
) -> RDIValidationResult:
    """Perform specific validation type"""
    validation_id = f"rdi_{int(datetime.now().timestamp())}_{validation_type.value}"
    standards = self.compliance_standards.get(validation_type.value, [])
    findings = []
    recommendations = []
    score = 0.0
    if validation_type == RDIValidationType.REQUIREMENTS_TRACEABILITY:
        findings, recommendations, score = self._validate_requirements_traceability(
            component_data, standards
        )
    elif validation_type == RDIValidationType.IMPLEMENTATION_QUALITY:
        findings, recommendations, score = self._validate_implementation_quality(
            component_data, standards
        )
    elif validation_type == RDIValidationType.SYSTEMATIC_APPROACH:
        findings, recommendations, score = self._validate_systematic_approach(
            component_data, standards
        )
    elif validation_type == RDIValidationType.PREVENTION_MEASURES:
        findings, recommendations, score = self._validate_prevention_measures(
            component_data, standards
        )
    elif validation_type == RDIValidationType.CONTINUOUS_IMPROVEMENT:
        findings, recommendations, score = self._validate_continuous_improvement(
            component_data, standards
        )
    compliance_level = self._determine_compliance_level(score)
    return RDIValidationResult(
        validation_id=validation_id,
        component_name=component_name,
        validation_type=validation_type,
        compliance_level=compliance_level,
        score=score,
        findings=findings,
        recommendations=recommendations,
        validation_timestamp=datetime.now(),
        validator="RDI Validator",
    )


def _determine_compliance_level(self, score: float) -> RDIComplianceLevel:
    """Determine compliance level based on score"""
    if score >= 0.9:
        return RDIComplianceLevel.EXCELLENT
    elif score >= 0.7:
        return RDIComplianceLevel.COMPLIANT
    elif score >= 0.5:
        return RDIComplianceLevel.PARTIALLY_COMPLIANT
    else:
        return RDIComplianceLevel.NON_COMPLIANT


def get_compliance_summary(self) -> Dict[str, Any]:
    """Get overall compliance summary"""
    if not self.validation_history:
        return {"message": "No validations performed yet"}
    total_validations = len(self.validation_history)
    excellent_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.EXCELLENT
        )
    )
    compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.COMPLIANT
        )
    )
    partially_compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.PARTIALLY_COMPLIANT
        )
    )
    non_compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.NON_COMPLIANT
        )
    )
    average_score = sum((v.score for v in self.validation_history)) / total_validations
    return {
        "total_validations": total_validations,
        "excellent": excellent_count,
        "compliant": compliant_count,
        "partially_compliant": partially_compliant_count,
        "non_compliant": non_compliant_count,
        "average_score": average_score,
        "compliance_rate": (excellent_count + compliant_count) / total_validations,
    }


def generate_improvement_plan(self) -> List[str]:
    """Generate improvement plan based on validation results"""
    plan = []
    all_recommendations = []
    for validation in self.validation_history:
        all_recommendations.extend(validation.recommendations)
    recommendation_counts = {}
    for rec in all_recommendations:
        recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
    sorted_recommendations = sorted(
        recommendation_counts.items(), key=lambda x: x[1], reverse=True
    )
    for rec, count in sorted_recommendations[:10]:
        plan.append(f"Priority {len(plan) + 1}: {rec} (appears in {count} validations)")
    return plan


def __init__(self):
    """Initialize RDI validator"""
    self.validation_history: List[RDIValidationResult] = []
    self.compliance_standards: Dict[str, List[str]] = {}
    self.improvement_recommendations: List[str] = []
    self._initialize_compliance_standards()
    logger.info("RDI Validator initialized")


def _initialize_compliance_standards(self):
    """Initialize RDI compliance standards"""
    self.compliance_standards = {
        "requirements_traceability": [
            "All features traceable to requirements",
            "Requirements documented and accessible",
            "Implementation matches requirements",
            "Changes tracked and validated",
        ],
        "implementation_quality": [
            "Code follows systematic principles",
            "Proper error handling implemented",
            "Comprehensive testing coverage",
            "Documentation is complete and accurate",
        ],
        "systematic_approach": [
            "Systematic development process followed",
            "Quality gates implemented",
            "Automated validation in place",
            "Continuous monitoring active",
        ],
        "prevention_measures": [
            "Prevention systems implemented",
            "Issue detection automated",
            "Learning systems in place",
            "Continuous improvement active",
        ],
        "continuous_improvement": [
            "Metrics collection implemented",
            "Feedback loops established",
            "Learning from failures",
            "Process optimization ongoing",
        ],
    }


def _perform_validation(
    self,
    component_name: str,
    component_data: Dict[str, Any],
    validation_type: RDIValidationType,
) -> RDIValidationResult:
    """Perform specific validation type"""
    validation_id = f"rdi_{int(datetime.now().timestamp())}_{validation_type.value}"
    standards = self.compliance_standards.get(validation_type.value, [])
    findings = []
    recommendations = []
    score = 0.0
    if validation_type == RDIValidationType.REQUIREMENTS_TRACEABILITY:
        findings, recommendations, score = self._validate_requirements_traceability(
            component_data, standards
        )
    elif validation_type == RDIValidationType.IMPLEMENTATION_QUALITY:
        findings, recommendations, score = self._validate_implementation_quality(
            component_data, standards
        )
    elif validation_type == RDIValidationType.SYSTEMATIC_APPROACH:
        findings, recommendations, score = self._validate_systematic_approach(
            component_data, standards
        )
    elif validation_type == RDIValidationType.PREVENTION_MEASURES:
        findings, recommendations, score = self._validate_prevention_measures(
            component_data, standards
        )
    elif validation_type == RDIValidationType.CONTINUOUS_IMPROVEMENT:
        findings, recommendations, score = self._validate_continuous_improvement(
            component_data, standards
        )
    compliance_level = self._determine_compliance_level(score)
    return RDIValidationResult(
        validation_id=validation_id,
        component_name=component_name,
        validation_type=validation_type,
        compliance_level=compliance_level,
        score=score,
        findings=findings,
        recommendations=recommendations,
        validation_timestamp=datetime.now(),
        validator="RDI Validator",
    )


def _determine_compliance_level(self, score: float) -> RDIComplianceLevel:
    """Determine compliance level based on score"""
    if score >= 0.9:
        return RDIComplianceLevel.EXCELLENT
    elif score >= 0.7:
        return RDIComplianceLevel.COMPLIANT
    elif score >= 0.5:
        return RDIComplianceLevel.PARTIALLY_COMPLIANT
    else:
        return RDIComplianceLevel.NON_COMPLIANT


def get_compliance_summary(self) -> Dict[str, Any]:
    """Get overall compliance summary"""
    if not self.validation_history:
        return {"message": "No validations performed yet"}
    total_validations = len(self.validation_history)
    excellent_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.EXCELLENT
        )
    )
    compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.COMPLIANT
        )
    )
    partially_compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.PARTIALLY_COMPLIANT
        )
    )
    non_compliant_count = sum(
        (
            1
            for v in self.validation_history
            if v.compliance_level == RDIComplianceLevel.NON_COMPLIANT
        )
    )
    average_score = sum((v.score for v in self.validation_history)) / total_validations
    return {
        "total_validations": total_validations,
        "excellent": excellent_count,
        "compliant": compliant_count,
        "partially_compliant": partially_compliant_count,
        "non_compliant": non_compliant_count,
        "average_score": average_score,
        "compliance_rate": (excellent_count + compliant_count) / total_validations,
    }


def generate_improvement_plan(self) -> List[str]:
    """Generate improvement plan based on validation results"""
    plan = []
    all_recommendations = []
    for validation in self.validation_history:
        all_recommendations.extend(validation.recommendations)
    recommendation_counts = {}
    for rec in all_recommendations:
        recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
    sorted_recommendations = sorted(
        recommendation_counts.items(), key=lambda x: x[1], reverse=True
    )
    for rec, count in sorted_recommendations[:10]:
        plan.append(f"Priority {len(plan) + 1}: {rec} (appears in {count} validations)")
    return plan
