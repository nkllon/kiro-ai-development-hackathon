"""
Beast Readiness Validator for OpenFlow Backlog Management System

This module implements comprehensive beast-readiness validation to ensure
backlog items are fully prepared for independent beast execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import BacklogItem, Requirement, AcceptanceCriterion, DependencyReference
from .enums import BeastReadinessStatus, ApprovalStatus


@dataclass(frozen=True)
class ValidationCriterion:
    """Individual validation criterion with scoring"""
    criterion_name: str
    description: str
    weight: float  # 0.0-1.0
    passed: bool
    score: float  # 0.0-1.0
    remediation_guidance: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompletenessReport:
    """Detailed completeness assessment report"""
    overall_score: float  # 0.0-1.0
    criteria_results: List[ValidationCriterion]
    missing_elements: List[str]
    remediation_actions: List[str]
    beast_ready: bool
    validation_timestamp: datetime
    
    def __post_init__(self):
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError("Overall score must be between 0.0 and 1.0")


@dataclass(frozen=True)
class DependencyStatus:
    """Dependency satisfaction status"""
    dependency_id: str
    target_item_id: str
    satisfied: bool
    satisfaction_evidence: str
    blocking_issues: List[str] = field(default_factory=list)
    estimated_resolution: Optional[datetime] = None


@dataclass(frozen=True)
class ReadinessValidation:
    """Complete beast-readiness validation result"""
    item_id: str
    validation_id: str
    completeness_report: CompletenessReport
    dependency_statuses: List[DependencyStatus]
    overall_beast_ready: bool
    confidence_score: float  # 0.0-1.0
    validation_timestamp: datetime
    validator_id: str
    next_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")


class BeastReadinessValidator(ReflectiveModule):
    """
    Validates backlog items for beast-readiness with comprehensive criteria checking.
    
    Ensures items meet all requirements for independent beast execution:
    - Complete requirements and acceptance criteria
    - All dependencies satisfied or explicitly documented
    - Testable and measurable success conditions
    - No ambiguous or interpretable elements
    """
    
    def __init__(self):
        super().__init__("BeastReadinessValidator")
        self._validation_cache: Dict[str, ReadinessValidation] = {}
        self._beast_readiness_threshold = 0.85  # 85% completeness required
        self._dependency_satisfaction_threshold = 0.90  # 90% dependencies must be satisfied
        
    def validate_beast_readiness(self, item: BacklogItem) -> ReadinessValidation:
        """
        Perform comprehensive beast-readiness validation.
        
        Args:
            item: BacklogItem to validate
            
        Returns:
            ReadinessValidation with detailed results and remediation guidance
        """
        try:
            validation_id = f"validation_{item.item_id}_{int(datetime.now().timestamp())}"
            
            # Perform completeness validation
            completeness_report = self.check_completeness_criteria(item)
            
            # Perform dependency validation
            dependency_statuses = self.verify_dependency_satisfaction(item)
            
            # Calculate overall readiness
            overall_ready = self._calculate_overall_readiness(
                completeness_report, dependency_statuses
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                completeness_report, dependency_statuses
            )
            
            # Generate next actions
            next_actions = self._generate_next_actions(
                completeness_report, dependency_statuses, overall_ready
            )
            
            validation = ReadinessValidation(
                item_id=item.item_id,
                validation_id=validation_id,
                completeness_report=completeness_report,
                dependency_statuses=dependency_statuses,
                overall_beast_ready=overall_ready,
                confidence_score=confidence,
                validation_timestamp=datetime.now(),
                validator_id=self.module_name,
                next_actions=next_actions
            )
            
            # Cache validation result
            self._validation_cache[item.item_id] = validation
            
            self._update_health_indicator(
                "validation_success",
                HealthStatus.HEALTHY,
                True,
                f"Successfully validated item {item.item_id}"
            )
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Beast readiness validation failed for {item.item_id}: {str(e)}")
            self._update_health_indicator(
                "validation_error",
                HealthStatus.UNHEALTHY,
                str(e),
                f"Validation failed for item {item.item_id}"
            )
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
        
        # Check requirements completeness
        req_criterion = self._validate_requirements_completeness(item.requirements)
        criteria_results.append(req_criterion)
        if not req_criterion.passed:
            missing_elements.extend(req_criterion.details.get("missing", []))
            remediation_actions.append(req_criterion.remediation_guidance)
        
        # Check acceptance criteria testability
        ac_criterion = self._validate_acceptance_criteria(item.acceptance_criteria)
        criteria_results.append(ac_criterion)
        if not ac_criterion.passed:
            missing_elements.extend(ac_criterion.details.get("missing", []))
            remediation_actions.append(ac_criterion.remediation_guidance)
        
        # Check context adequacy
        context_criterion = self._validate_context_adequacy(item)
        criteria_results.append(context_criterion)
        if not context_criterion.passed:
            missing_elements.extend(context_criterion.details.get("missing", []))
            remediation_actions.append(context_criterion.remediation_guidance)
        
        # Check for ambiguity
        ambiguity_criterion = self._validate_ambiguity_absence(item)
        criteria_results.append(ambiguity_criterion)
        if not ambiguity_criterion.passed:
            missing_elements.extend(ambiguity_criterion.details.get("ambiguous", []))
            remediation_actions.append(ambiguity_criterion.remediation_guidance)
        
        # Calculate overall completeness score
        total_weight = sum(c.weight for c in criteria_results)
        weighted_score = sum(c.score * c.weight for c in criteria_results)
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        beast_ready = overall_score >= self._beast_readiness_threshold
        
        return CompletenessReport(
            overall_score=overall_score,
            criteria_results=criteria_results,
            missing_elements=missing_elements,
            remediation_actions=remediation_actions,
            beast_ready=beast_ready,
            validation_timestamp=datetime.now()
        )
    
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
            # For now, we'll simulate dependency checking
            # In a real implementation, this would query the actual dependency system
            status = self._check_dependency_satisfaction(dep_ref, item)
            dependency_statuses.append(status)
        
        return dependency_statuses
    
    def _validate_requirements_completeness(self, requirements: List[Requirement]) -> ValidationCriterion:
        """Validate that requirements are complete and well-defined"""
        missing = []
        score = 1.0
        
        if not requirements:
            missing.append("No requirements defined")
            score = 0.0
        else:
            # Check each requirement for completeness
            for req in requirements:
                if not req.description or len(req.description.strip()) < 10:
                    missing.append(f"Requirement {req.requirement_id} has insufficient description")
                    score -= 0.2
                
                if not req.acceptance_criteria:
                    missing.append(f"Requirement {req.requirement_id} lacks acceptance criteria")
                    score -= 0.3
        
        score = max(0.0, score)
        passed = score >= 0.8 and not missing
        
        return ValidationCriterion(
            criterion_name="requirements_completeness",
            description="Requirements are complete, clear, and well-defined",
            weight=0.3,
            passed=passed,
            score=score,
            remediation_guidance="Add detailed descriptions and acceptance criteria for all requirements",
            details={"missing": missing, "requirement_count": len(requirements)}
        )
    
    def _validate_acceptance_criteria(self, criteria: List[AcceptanceCriterion]) -> ValidationCriterion:
        """Validate that acceptance criteria are testable and measurable"""
        missing = []
        score = 1.0
        
        if not criteria:
            missing.append("No acceptance criteria defined")
            score = 0.0
        else:
            for criterion in criteria:
                if not criterion.testable:
                    missing.append(f"Criterion {criterion.criterion_id} is not testable")
                    score -= 0.3
                
                if not criterion.measurable:
                    missing.append(f"Criterion {criterion.criterion_id} is not measurable")
                    score -= 0.3
                
                if not criterion.description or len(criterion.description.strip()) < 10:
                    missing.append(f"Criterion {criterion.criterion_id} has insufficient description")
                    score -= 0.2
        
        score = max(0.0, score)
        passed = score >= 0.8 and not missing
        
        return ValidationCriterion(
            criterion_name="acceptance_criteria_quality",
            description="Acceptance criteria are testable, measurable, and unambiguous",
            weight=0.3,
            passed=passed,
            score=score,
            remediation_guidance="Ensure all acceptance criteria are testable and measurable with clear descriptions",
            details={"missing": missing, "criteria_count": len(criteria)}
        )
    
    def _validate_context_adequacy(self, item: BacklogItem) -> ValidationCriterion:
        """Validate that item has adequate context for independent execution"""
        missing = []
        score = 1.0
        
        # Check title adequacy
        if not item.title or len(item.title.strip()) < 5:
            missing.append("Title is too short or missing")
            score -= 0.2
        
        # Check if MPM validation exists and is approved
        if not item.mpm_validation:
            missing.append("MPM validation is missing")
            score -= 0.4
        elif item.mpm_validation.approval_status != ApprovalStatus.APPROVED:
            missing.append("MPM validation is not approved")
            score -= 0.3
        
        # Check strategic track assignment
        if not item.track:
            missing.append("Strategic track not assigned")
            score -= 0.2
        
        score = max(0.0, score)
        passed = score >= 0.8 and not missing
        
        return ValidationCriterion(
            criterion_name="context_adequacy",
            description="Item has adequate context and supporting information",
            weight=0.2,
            passed=passed,
            score=score,
            remediation_guidance="Ensure item has clear title, approved MPM validation, and strategic track assignment",
            details={"missing": missing}
        )
    
    def _validate_ambiguity_absence(self, item: BacklogItem) -> ValidationCriterion:
        """Validate that item contains no ambiguous or interpretable elements"""
        ambiguous = []
        score = 1.0
        
        # Check for ambiguous words in title and requirements
        ambiguous_words = ["maybe", "probably", "should", "could", "might", "perhaps", "possibly"]
        
        # Check title
        title_lower = item.title.lower()
        for word in ambiguous_words:
            if word in title_lower:
                ambiguous.append(f"Ambiguous word '{word}' in title")
                score -= 0.1
        
        # Check requirements descriptions
        for req in item.requirements:
            desc_lower = req.description.lower()
            for word in ambiguous_words:
                if word in desc_lower:
                    ambiguous.append(f"Ambiguous word '{word}' in requirement {req.requirement_id}")
                    score -= 0.1
        
        # Check acceptance criteria
        for criterion in item.acceptance_criteria:
            desc_lower = criterion.description.lower()
            for word in ambiguous_words:
                if word in desc_lower:
                    ambiguous.append(f"Ambiguous word '{word}' in acceptance criterion {criterion.criterion_id}")
                    score -= 0.1
        
        score = max(0.0, score)
        passed = score >= 0.9 and not ambiguous
        
        return ValidationCriterion(
            criterion_name="ambiguity_absence",
            description="Item contains no ambiguous or interpretable language",
            weight=0.2,
            passed=passed,
            score=score,
            remediation_guidance="Remove ambiguous language and replace with specific, measurable terms",
            details={"ambiguous": ambiguous}
        )
    
    def _check_dependency_satisfaction(self, dep_ref: DependencyReference, item: BacklogItem) -> DependencyStatus:
        """Check if a specific dependency is satisfied"""
        # This is a simplified implementation
        # In reality, this would check the actual status of the target item
        
        # For now, assume dependencies are satisfied if they have clear descriptions
        satisfied = bool(dep_ref.description and len(dep_ref.description.strip()) > 10)
        
        blocking_issues = []
        if not satisfied:
            blocking_issues.append("Dependency description is insufficient")
        
        evidence = dep_ref.description if satisfied else "No clear satisfaction criteria"
        
        return DependencyStatus(
            dependency_id=dep_ref.dependency_id,
            target_item_id=dep_ref.target_item_id,
            satisfied=satisfied,
            satisfaction_evidence=evidence,
            blocking_issues=blocking_issues,
            estimated_resolution=None  # Would be calculated based on target item status
        )
    
    def _calculate_overall_readiness(
        self, 
        completeness: CompletenessReport, 
        dependencies: List[DependencyStatus]
    ) -> bool:
        """Calculate overall beast-readiness based on completeness and dependencies"""
        
        # Must meet completeness threshold
        if not completeness.beast_ready:
            return False
        
        # Check dependency satisfaction rate
        if dependencies:
            satisfied_count = sum(1 for dep in dependencies if dep.satisfied)
            satisfaction_rate = satisfied_count / len(dependencies)
            
            if satisfaction_rate < self._dependency_satisfaction_threshold:
                return False
        
        return True
    
    def _calculate_confidence_score(
        self, 
        completeness: CompletenessReport, 
        dependencies: List[DependencyStatus]
    ) -> float:
        """Calculate confidence score for the validation"""
        
        # Base confidence from completeness score
        confidence = completeness.overall_score * 0.7
        
        # Add dependency satisfaction contribution
        if dependencies:
            satisfied_count = sum(1 for dep in dependencies if dep.satisfied)
            dep_score = satisfied_count / len(dependencies)
            confidence += dep_score * 0.3
        else:
            confidence += 0.3  # No dependencies is good
        
        return min(1.0, confidence)
    
    def _generate_next_actions(
        self, 
        completeness: CompletenessReport, 
        dependencies: List[DependencyStatus],
        overall_ready: bool
    ) -> List[str]:
        """Generate specific next actions based on validation results"""
        actions = []
        
        if not overall_ready:
            actions.extend(completeness.remediation_actions)
            
            # Add dependency-specific actions
            for dep in dependencies:
                if not dep.satisfied:
                    actions.append(f"Resolve dependency {dep.dependency_id}: {', '.join(dep.blocking_issues)}")
        
        if not actions:
            actions.append("Item is beast-ready and can be released to execution pool")
        
        return actions
    
    # ReflectiveModule interface implementation
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get operational status for external queries"""
        return {
            "module_name": self.module_name,
            "status": "operational",
            "cached_validations": len(self._validation_cache),
            "beast_readiness_threshold": self._beast_readiness_threshold,
            "dependency_satisfaction_threshold": self._dependency_satisfaction_threshold,
            "health_indicators": {name: indicator.status.value for name, indicator in self._health_indicators.items()},
            "degradation_active": self._degradation_active
        }
    
    def is_healthy(self) -> bool:
        """Check if validator is healthy"""
        if not self._health_indicators:
            return True
        
        unhealthy_count = sum(
            1 for indicator in self._health_indicators.values() 
            if indicator.status == HealthStatus.UNHEALTHY
        )
        
        return unhealthy_count == 0
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health metrics"""
        return {
            "total_indicators": len(self._health_indicators),
            "indicators": {
                name: {
                    "status": indicator.status.value,
                    "value": indicator.value,
                    "message": indicator.message,
                    "timestamp": indicator.timestamp
                }
                for name, indicator in self._health_indicators.items()
            },
            "overall_health": self.is_healthy()
        }
    
    def _get_primary_responsibility(self) -> str:
        """Define primary responsibility"""
        return "Validate backlog items for beast-readiness with comprehensive criteria checking"