"""
Requirements Manager - Systematic creation and management of comprehensive requirements.

Handles EARS format validation, user story templates, and acceptance criteria generation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import re

from ..core.base import ReflectiveModule
from ..core.models import (
    Requirement,
    RequirementStatus,
    UserStory,
    AcceptanceCriterion,
    EARSStatement,
    ValidationMethod,
    Priority,
    SecurityImplication,
    PerformanceImplication,
    ComplianceTag
)


logger = logging.getLogger(__name__)


class RequirementsManager(ReflectiveModule):
    """
    Systematic creation and management of comprehensive requirements.
    
    Provides EARS format enforcement, user story templates, and systematic
    validation based on RM-DDD proven patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the requirements manager."""
        super().__init__()
        self._config = config or {}
        self._role_library = self._initialize_role_library()
        self._ears_patterns = self._initialize_ears_patterns()
        self._validation_templates = self._initialize_validation_templates()
        
        logger.info("RequirementsManager initialized with systematic validation")
    
    def _initialize_role_library(self) -> List[str]:
        """Initialize role library based on RM-DDD patterns."""
        return [
            "developer",
            "system architect", 
            "project manager",
            "quality assurance engineer",
            "team lead",
            "compliance officer",
            "technical writer",
            "ecosystem integrator",
            "performance engineer",
            "security architect",
            "end user",
            "administrator",
            "business analyst",
            "product owner"
        ]
    
    def _initialize_ears_patterns(self) -> Dict[str, str]:
        """Initialize EARS format patterns for validation."""
        return {
            'when_pattern': r'^WHEN\s+(.+)\s+THEN\s+(.+)\s+SHALL\s+(.+)$',
            'if_pattern': r'^IF\s+(.+)\s+THEN\s+(.+)\s+SHALL\s+(.+)$',
            'while_pattern': r'^WHILE\s+(.+)\s+THEN\s+(.+)\s+SHALL\s+(.+)$'
        }
    
    def _initialize_validation_templates(self) -> Dict[str, ValidationMethod]:
        """Initialize validation method templates."""
        return {
            'automated_test': ValidationMethod(
                method_type="automated_test",
                description="Automated test validation",
                tools=["pytest", "junit", "jest"],
                success_criteria="Test passes with expected results"
            ),
            'manual_test': ValidationMethod(
                method_type="manual_test", 
                description="Manual test validation",
                tools=["test_plan", "checklist"],
                success_criteria="Manual verification confirms expected behavior"
            ),
            'code_review': ValidationMethod(
                method_type="review",
                description="Code review validation",
                tools=["pull_request", "review_checklist"],
                success_criteria="Code review approves implementation"
            ),
            'measurement': ValidationMethod(
                method_type="measurement",
                description="Quantitative measurement validation",
                tools=["metrics", "monitoring"],
                success_criteria="Measurements meet specified criteria"
            )
        }
    
    def create_requirement(
        self,
        role: str,
        feature: str,
        benefit: str,
        business_value: str = "",
        priority: Priority = Priority.MEDIUM
    ) -> Requirement:
        """
        Create a new requirement with systematic structure.
        
        Args:
            role: User role for the user story
            feature: Feature description
            benefit: Benefit description
            business_value: Business value description
            priority: Requirement priority
            
        Returns:
            New requirement instance
        """
        # Validate role
        if not self._validate_role(role):
            logger.warning(f"Role '{role}' not in standard role library")
        
        # Create user story
        user_story = UserStory(
            role=role,
            feature=feature,
            benefit=benefit
        )
        
        # Create requirement
        requirement = Requirement(
            user_story=user_story,
            business_value=business_value,
            priority=priority,
            status=RequirementStatus.DRAFT
        )
        
        logger.info(f"Created requirement: {user_story}")
        return requirement
    
    def _validate_role(self, role: str) -> bool:
        """Validate if role is in the standard role library."""
        return role.lower() in [r.lower() for r in self._role_library]
    
    def add_acceptance_criterion(
        self,
        requirement: Requirement,
        condition: str,
        system: str,
        response: str,
        statement_type: str = "WHEN",
        validation_method: Optional[str] = None
    ) -> bool:
        """
        Add acceptance criterion with EARS format validation.
        
        Args:
            requirement: Requirement to add criterion to
            condition: Condition part of EARS statement
            system: System part of EARS statement
            response: Response part of EARS statement
            statement_type: Type of EARS statement (WHEN, IF, WHILE)
            validation_method: Validation method key
            
        Returns:
            True if criterion was added successfully
        """
        # Create EARS statement
        ears_statement = EARSStatement(
            condition=condition,
            system=system,
            response=response,
            statement_type=statement_type
        )
        
        # Validate EARS format
        if not self._validate_ears_format(ears_statement):
            logger.error(f"Invalid EARS format: {ears_statement}")
            return False
        
        # Get validation method
        validation = self._get_validation_method(validation_method)
        
        # Create acceptance criterion
        criterion = AcceptanceCriterion(
            ears_format=ears_statement,
            testable=True,
            validation_method=validation
        )
        
        # Add to requirement
        requirement.add_acceptance_criterion(criterion)
        
        logger.info(f"Added acceptance criterion to requirement {requirement.id}")
        return True
    
    def _validate_ears_format(self, ears_statement: EARSStatement) -> bool:
        """
        Validate EARS format statement.
        
        Args:
            ears_statement: EARS statement to validate
            
        Returns:
            True if format is valid
        """
        # Check that all parts are present
        if not (ears_statement.condition and ears_statement.system and ears_statement.response):
            return False
        
        # Check statement type
        if ears_statement.statement_type not in ["WHEN", "IF", "WHILE"]:
            return False
        
        # Validate against patterns
        full_statement = str(ears_statement)
        pattern_key = f"{ears_statement.statement_type.lower()}_pattern"
        
        if pattern_key in self._ears_patterns:
            pattern = self._ears_patterns[pattern_key]
            if not re.match(pattern, full_statement, re.IGNORECASE):
                return False
        
        return True
    
    def _get_validation_method(self, method_key: Optional[str]) -> ValidationMethod:
        """Get validation method template or create default."""
        if method_key and method_key in self._validation_templates:
            return self._validation_templates[method_key]
        else:
            return self._validation_templates['automated_test']  # Default
    
    def validate_requirement_completeness(self, requirement: Requirement) -> Dict[str, bool]:
        """
        Validate requirement completeness against systematic standards.
        
        Args:
            requirement: Requirement to validate
            
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        # User story validation
        user_story = requirement.user_story
        validation_results['has_role'] = bool(user_story.role)
        validation_results['has_feature'] = bool(user_story.feature)
        validation_results['has_benefit'] = bool(user_story.benefit)
        validation_results['role_is_valid'] = self._validate_role(user_story.role)
        
        # Acceptance criteria validation
        validation_results['has_acceptance_criteria'] = len(requirement.acceptance_criteria) > 0
        validation_results['all_criteria_testable'] = all(
            ac.testable for ac in requirement.acceptance_criteria
        )
        validation_results['all_criteria_have_ears'] = all(
            self._validate_ears_format(ac.ears_format) for ac in requirement.acceptance_criteria
        )
        
        # Business value validation
        validation_results['has_business_value'] = bool(requirement.business_value)
        
        # Overall completeness
        validation_results['is_complete'] = all(validation_results.values())
        
        return validation_results
    
    def generate_acceptance_criteria_suggestions(
        self,
        requirement: Requirement
    ) -> List[Dict[str, str]]:
        """
        Generate acceptance criteria suggestions based on user story.
        
        Args:
            requirement: Requirement to generate suggestions for
            
        Returns:
            List of suggested acceptance criteria
        """
        suggestions = []
        user_story = requirement.user_story
        
        # Basic functionality suggestion
        suggestions.append({
            'condition': f"the {user_story.role} requests {user_story.feature}",
            'system': "the system",
            'response': f"provide {user_story.feature} functionality",
            'statement_type': "WHEN"
        })
        
        # Error handling suggestion
        suggestions.append({
            'condition': f"the {user_story.feature} request fails",
            'system': "the system", 
            'response': "provide clear error message and recovery options",
            'statement_type': "WHEN"
        })
        
        # Validation suggestion
        suggestions.append({
            'condition': f"invalid input is provided for {user_story.feature}",
            'system': "the system",
            'response': "reject the input and provide validation feedback",
            'statement_type': "WHEN"
        })
        
        return suggestions
    
    def add_security_implication(
        self,
        requirement: Requirement,
        threat_category: str,
        risk_level: str,
        mitigation_strategy: str,
        compliance_requirements: Optional[List[str]] = None
    ) -> None:
        """
        Add security implication to requirement.
        
        Args:
            requirement: Requirement to add security implication to
            threat_category: Category of security threat
            risk_level: Risk level (low, medium, high, critical)
            mitigation_strategy: Strategy to mitigate the risk
            compliance_requirements: List of compliance requirements
        """
        security_implication = SecurityImplication(
            threat_category=threat_category,
            risk_level=risk_level,
            mitigation_strategy=mitigation_strategy,
            compliance_requirements=compliance_requirements or []
        )
        
        requirement.security_implications.append(security_implication)
        requirement.updated_at = datetime.now()
        
        logger.info(f"Added security implication to requirement {requirement.id}")
    
    def add_performance_implication(
        self,
        requirement: Requirement,
        metric_type: str,
        expected_impact: str,
        measurement_method: str,
        target_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add performance implication to requirement.
        
        Args:
            requirement: Requirement to add performance implication to
            metric_type: Type of performance metric
            expected_impact: Expected performance impact
            measurement_method: Method to measure performance
            target_values: Target performance values
        """
        from ..core.models import PerformanceMetricType
        
        # Convert string to enum
        try:
            metric_enum = PerformanceMetricType(metric_type.lower())
        except ValueError:
            metric_enum = PerformanceMetricType.LATENCY  # Default
        
        performance_implication = PerformanceImplication(
            metric_type=metric_enum,
            expected_impact=expected_impact,
            measurement_method=measurement_method,
            target_values=target_values or {}
        )
        
        requirement.performance_implications.append(performance_implication)
        requirement.updated_at = datetime.now()
        
        logger.info(f"Added performance implication to requirement {requirement.id}")
    
    def add_compliance_tag(
        self,
        requirement: Requirement,
        framework: str,
        requirement_id: str,
        compliance_level: str,
        validation_required: bool = True
    ) -> None:
        """
        Add compliance tag to requirement.
        
        Args:
            requirement: Requirement to add compliance tag to
            framework: Compliance framework (e.g., SOX, GDPR, HIPAA)
            requirement_id: ID within the compliance framework
            compliance_level: Level of compliance required
            validation_required: Whether validation is required
        """
        compliance_tag = ComplianceTag(
            framework=framework,
            requirement_id=requirement_id,
            compliance_level=compliance_level,
            validation_required=validation_required
        )
        
        requirement.compliance_tags.append(compliance_tag)
        requirement.updated_at = datetime.now()
        
        logger.info(f"Added compliance tag {framework} to requirement {requirement.id}")
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the requirements manager."""
        return {
            "status": "healthy",
            "role_library_size": len(self._role_library),
            "ears_patterns_loaded": len(self._ears_patterns),
            "validation_templates_loaded": len(self._validation_templates),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if requirements manager is ready for operation."""
        return (
            len(self._role_library) > 0 and
            len(self._ears_patterns) > 0 and
            len(self._validation_templates) > 0
        )
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "role_library_size": float(len(self._role_library)),
            "ears_patterns_count": float(len(self._ears_patterns)),
            "validation_templates_count": float(len(self._validation_templates))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"