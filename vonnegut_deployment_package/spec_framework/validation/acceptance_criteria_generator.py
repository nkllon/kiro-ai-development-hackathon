"""
Acceptance Criteria Generator - Systematic generation and validation of acceptance criteria.

Creates systematic acceptance criteria generation from user stories with testability
validation and templates based on RM-DDD patterns.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import AcceptanceCriterion, EARSStatement, ValidationMethod, UserStory
from .ears_validator import EARSFormatValidator


logger = logging.getLogger(__name__)


class AcceptanceCriteriaValidationSeverity(Enum):
    """Severity levels for acceptance criteria validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AcceptanceCriteriaValidationIssue:
    """Individual validation issue for acceptance criteria."""
    severity: AcceptanceCriteriaValidationSeverity
    criterion_index: int
    message: str
    suggestion: Optional[str] = None


@dataclass
class AcceptanceCriteriaValidationResult:
    """Result of acceptance criteria validation."""
    is_valid: bool
    criteria_count: int
    testable_count: int
    issues: List[AcceptanceCriteriaValidationIssue] = None
    suggestions: List[str] = None
    testability_score: float = 0.0  # 0-100 score for overall testability
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []


class AcceptanceCriteriaGenerator(ReflectiveModule):
    """
    Acceptance Criteria Generator.
    
    Provides systematic generation of acceptance criteria from user stories
    with testability validation and systematic guidance based on RM-DDD patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the acceptance criteria generator."""
        super().__init__()
        self._config = config or {}
        self._ears_validator = EARSFormatValidator()
        self._criteria_templates = self._initialize_criteria_templates()
        self._testability_patterns = self._initialize_testability_patterns()
        self._validation_methods = self._initialize_validation_methods()
        
        logger.info("AcceptanceCriteriaGenerator initialized with systematic templates")
    
    def _initialize_criteria_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize acceptance criteria templates based on RM-DDD patterns."""
        return {
            'basic_functionality': [
                {
                    'condition': 'user provides valid input',
                    'system': 'the system',
                    'response': 'process the input and return expected results',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'user provides invalid input',
                    'system': 'the system',
                    'response': 'reject the input and provide clear validation feedback',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'the operation completes successfully',
                    'system': 'the system',
                    'response': 'provide confirmation and any relevant output',
                    'statement_type': 'WHEN'
                }
            ],
            'error_handling': [
                {
                    'condition': 'an error occurs during processing',
                    'system': 'the system',
                    'response': 'log the error and provide user-friendly error message',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'the system is unavailable',
                    'system': 'the system',
                    'response': 'display appropriate unavailability message and retry options',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'invalid data is encountered',
                    'system': 'the system',
                    'response': 'halt processing and report specific validation errors',
                    'statement_type': 'WHEN'
                }
            ],
            'security': [
                {
                    'condition': 'user is not authenticated',
                    'system': 'the system',
                    'response': 'redirect to authentication and deny access to protected resources',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'user lacks required permissions',
                    'system': 'the system',
                    'response': 'deny access and display appropriate authorization message',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'suspicious activity is detected',
                    'system': 'the system',
                    'response': 'log the activity and apply appropriate security measures',
                    'statement_type': 'WHEN'
                }
            ],
            'performance': [
                {
                    'condition': 'processing large datasets',
                    'system': 'the system',
                    'response': 'complete operations within acceptable time limits',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'multiple concurrent users access the system',
                    'system': 'the system',
                    'response': 'maintain responsive performance for all users',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'system resources are constrained',
                    'system': 'the system',
                    'response': 'gracefully degrade performance while maintaining core functionality',
                    'statement_type': 'WHEN'
                }
            ],
            'usability': [
                {
                    'condition': 'user completes the workflow',
                    'system': 'the system',
                    'response': 'provide clear confirmation and next steps',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'user needs help',
                    'system': 'the system',
                    'response': 'provide contextual help and guidance',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'user makes a mistake',
                    'system': 'the system',
                    'response': 'provide clear recovery options and prevent data loss',
                    'statement_type': 'WHEN'
                }
            ],
            'integration': [
                {
                    'condition': 'external service is unavailable',
                    'system': 'the system',
                    'response': 'handle the failure gracefully and provide fallback options',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'data synchronization is required',
                    'system': 'the system',
                    'response': 'ensure data consistency across all integrated systems',
                    'statement_type': 'WHEN'
                },
                {
                    'condition': 'external data format changes',
                    'system': 'the system',
                    'response': 'adapt to format changes or provide clear error messages',
                    'statement_type': 'WHEN'
                }
            ]
        }
    
    def _initialize_testability_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for testability validation."""
        return {
            'testable_verbs': [
                'return', 'display', 'show', 'create', 'update', 'delete', 'send',
                'receive', 'validate', 'reject', 'accept', 'log', 'store', 'retrieve',
                'calculate', 'generate', 'process', 'transform', 'notify', 'redirect',
                'save', 'load', 'export', 'import', 'format', 'parse', 'encrypt',
                'decrypt', 'compress', 'decompress', 'sort', 'filter', 'search'
            ],
            'measurable_outcomes': [
                'within', 'less than', 'greater than', 'exactly', 'at least', 'at most',
                'between', 'contains', 'includes', 'excludes', 'matches', 'equals',
                'differs from', 'increases', 'decreases', 'maintains', 'preserves'
            ],
            'observable_states': [
                'visible', 'hidden', 'enabled', 'disabled', 'active', 'inactive',
                'selected', 'unselected', 'expanded', 'collapsed', 'open', 'closed',
                'available', 'unavailable', 'valid', 'invalid', 'complete', 'incomplete'
            ],
            'vague_terms': [
                'appropriately', 'properly', 'correctly', 'successfully', 'effectively',
                'efficiently', 'well', 'good', 'bad', 'better', 'worse', 'nice',
                'clean', 'smooth', 'fast', 'slow', 'easy', 'hard', 'simple', 'complex'
            ]
        }
    
    def _initialize_validation_methods(self) -> Dict[str, ValidationMethod]:
        """Initialize validation method templates."""
        return {
            'unit_test': ValidationMethod(
                method_type="automated_test",
                description="Unit test validation",
                tools=["pytest", "junit", "jest", "mocha"],
                success_criteria="Unit tests pass with expected assertions"
            ),
            'integration_test': ValidationMethod(
                method_type="automated_test",
                description="Integration test validation",
                tools=["pytest", "postman", "selenium", "cypress"],
                success_criteria="Integration tests verify end-to-end functionality"
            ),
            'ui_test': ValidationMethod(
                method_type="automated_test",
                description="UI test validation",
                tools=["selenium", "cypress", "playwright", "puppeteer"],
                success_criteria="UI tests verify user interface behavior"
            ),
            'api_test': ValidationMethod(
                method_type="automated_test",
                description="API test validation",
                tools=["postman", "rest-assured", "supertest"],
                success_criteria="API tests verify service endpoints and responses"
            ),
            'manual_test': ValidationMethod(
                method_type="manual_test",
                description="Manual test validation",
                tools=["test_plan", "checklist", "exploratory_testing"],
                success_criteria="Manual verification confirms expected behavior"
            ),
            'performance_test': ValidationMethod(
                method_type="measurement",
                description="Performance test validation",
                tools=["jmeter", "k6", "artillery", "locust"],
                success_criteria="Performance metrics meet specified criteria"
            ),
            'security_test': ValidationMethod(
                method_type="automated_test",
                description="Security test validation",
                tools=["owasp_zap", "burp_suite", "nessus"],
                success_criteria="Security tests verify protection against known vulnerabilities"
            )
        }
    
    def generate_acceptance_criteria(
        self,
        user_story: UserStory,
        include_categories: Optional[List[str]] = None,
        custom_criteria: Optional[List[Dict[str, str]]] = None
    ) -> List[AcceptanceCriterion]:
        """
        Generate acceptance criteria from user story.
        
        Args:
            user_story: User story to generate criteria for
            include_categories: Categories of criteria to include
            custom_criteria: Additional custom criteria templates
            
        Returns:
            List of generated acceptance criteria
        """
        criteria = []
        
        # Default categories if none specified
        if include_categories is None:
            include_categories = ['basic_functionality', 'error_handling']
        
        # Generate criteria from templates
        for category in include_categories:
            if category in self._criteria_templates:
                category_criteria = self._generate_category_criteria(
                    user_story, category
                )
                criteria.extend(category_criteria)
        
        # Add custom criteria if provided
        if custom_criteria:
            for custom_template in custom_criteria:
                criterion = self._create_criterion_from_template(
                    custom_template, user_story
                )
                if criterion:
                    criteria.append(criterion)
        
        # Generate role-specific criteria
        role_criteria = self._generate_role_specific_criteria(user_story)
        criteria.extend(role_criteria)
        
        # Generate feature-specific criteria
        feature_criteria = self._generate_feature_specific_criteria(user_story)
        criteria.extend(feature_criteria)
        
        logger.info(f"Generated {len(criteria)} acceptance criteria for user story")
        return criteria
    
    def _generate_category_criteria(
        self,
        user_story: UserStory,
        category: str
    ) -> List[AcceptanceCriterion]:
        """Generate criteria for a specific category."""
        criteria = []
        templates = self._criteria_templates.get(category, [])
        
        for template in templates:
            criterion = self._create_criterion_from_template(template, user_story)
            if criterion:
                criteria.append(criterion)
        
        return criteria
    
    def _create_criterion_from_template(
        self,
        template: Dict[str, str],
        user_story: UserStory
    ) -> Optional[AcceptanceCriterion]:
        """Create acceptance criterion from template."""
        try:
            # Customize template based on user story
            customized_template = self._customize_template(template, user_story)
            
            # Create EARS statement
            ears_statement = EARSStatement(
                condition=customized_template['condition'],
                system=customized_template['system'],
                response=customized_template['response'],
                statement_type=customized_template.get('statement_type', 'WHEN')
            )
            
            # Validate EARS format
            validation_result = self._ears_validator.validate_ears_statement(str(ears_statement))
            
            # Determine validation method
            validation_method = self._determine_validation_method(customized_template)
            
            # Create acceptance criterion
            criterion = AcceptanceCriterion(
                ears_format=ears_statement,
                testable=validation_result.is_valid,
                validation_method=validation_method
            )
            
            return criterion
            
        except Exception as e:
            logger.warning(f"Failed to create criterion from template: {e}")
            return None
    
    def _customize_template(
        self,
        template: Dict[str, str],
        user_story: UserStory
    ) -> Dict[str, str]:
        """Customize template based on user story context."""
        customized = template.copy()
        
        # Extract key terms from user story
        feature_terms = self._extract_feature_terms(user_story.feature)
        role_context = self._get_role_context(user_story.role)
        
        # Customize condition
        condition = customized['condition']
        if 'user' in condition and feature_terms:
            # Replace generic "user" with specific action context
            main_action = feature_terms.get('main_action', 'interacts with')
            condition = condition.replace(
                'user provides valid input',
                f'{user_story.role} provides valid {main_action} input'
            )
            condition = condition.replace(
                'user provides invalid input',
                f'{user_story.role} provides invalid {main_action} input'
            )
        
        # Customize system
        system = customized['system']
        if system == 'the system' and feature_terms:
            target_system = feature_terms.get('target_system', 'the system')
            system = target_system
        
        # Customize response based on feature
        response = customized['response']
        if feature_terms and 'main_action' in feature_terms:
            action = feature_terms['main_action']
            if 'process the input' in response:
                response = response.replace(
                    'process the input',
                    f'{action} the input'
                )
        
        return {
            'condition': condition,
            'system': system,
            'response': response,
            'statement_type': customized.get('statement_type', 'WHEN')
        }
    
    def _extract_feature_terms(self, feature: str) -> Dict[str, str]:
        """Extract key terms from feature description."""
        terms = {}
        
        # Extract main action verb
        action_verbs = [
            'create', 'update', 'delete', 'view', 'search', 'filter', 'sort',
            'export', 'import', 'configure', 'manage', 'monitor', 'analyze',
            'validate', 'approve', 'reject', 'submit', 'process', 'generate',
            'run', 'execute', 'start', 'stop', 'pause', 'resume'
        ]
        
        feature_lower = feature.lower()
        for verb in action_verbs:
            if verb in feature_lower:
                terms['main_action'] = verb
                break
        
        # Extract target system/object
        system_indicators = [
            'test', 'report', 'dashboard', 'form', 'data', 'file', 'document',
            'user', 'account', 'profile', 'setting', 'configuration', 'backup',
            'database', 'service', 'api', 'interface', 'system', 'application'
        ]
        
        for indicator in system_indicators:
            if indicator in feature_lower:
                terms['target_system'] = f"{indicator} service"
                break
        
        return terms
    
    def _get_role_context(self, role: str) -> Dict[str, Any]:
        """Get context information for role."""
        role_contexts = {
            'developer': {
                'typical_systems': ['IDE', 'build system', 'test framework'],
                'common_actions': ['debug', 'test', 'build', 'deploy'],
                'validation_preference': 'automated_test'
            },
            'administrator': {
                'typical_systems': ['admin panel', 'management console', 'monitoring system'],
                'common_actions': ['configure', 'monitor', 'manage', 'backup'],
                'validation_preference': 'manual_test'
            },
            'end user': {
                'typical_systems': ['user interface', 'web application', 'mobile app'],
                'common_actions': ['view', 'create', 'update', 'search'],
                'validation_preference': 'ui_test'
            }
        }
        
        return role_contexts.get(role.lower(), {
            'typical_systems': ['system'],
            'common_actions': ['interact'],
            'validation_preference': 'manual_test'
        })
    
    def _generate_role_specific_criteria(self, user_story: UserStory) -> List[AcceptanceCriterion]:
        """Generate criteria specific to the user role."""
        criteria = []
        role_context = self._get_role_context(user_story.role)
        
        # Generate authentication/authorization criteria for non-public roles
        if user_story.role.lower() not in ['end user', 'guest', 'visitor']:
            auth_template = {
                'condition': f'{user_story.role} is not authenticated',
                'system': 'the system',
                'response': 'deny access and redirect to authentication',
                'statement_type': 'WHEN'
            }
            
            auth_criterion = self._create_criterion_from_template(auth_template, user_story)
            if auth_criterion:
                criteria.append(auth_criterion)
        
        return criteria
    
    def _generate_feature_specific_criteria(self, user_story: UserStory) -> List[AcceptanceCriterion]:
        """Generate criteria specific to the feature."""
        criteria = []
        feature_lower = user_story.feature.lower()
        
        # Generate data validation criteria for data-related features
        if any(term in feature_lower for term in ['create', 'update', 'submit', 'save']):
            validation_template = {
                'condition': 'required fields are missing',
                'system': 'the system',
                'response': 'highlight missing fields and prevent submission',
                'statement_type': 'WHEN'
            }
            
            validation_criterion = self._create_criterion_from_template(validation_template, user_story)
            if validation_criterion:
                criteria.append(validation_criterion)
        
        # Generate search criteria for search features
        if any(term in feature_lower for term in ['search', 'find', 'filter']):
            search_template = {
                'condition': 'no results match the search criteria',
                'system': 'the system',
                'response': 'display "no results found" message with search suggestions',
                'statement_type': 'WHEN'
            }
            
            search_criterion = self._create_criterion_from_template(search_template, user_story)
            if search_criterion:
                criteria.append(search_criterion)
        
        return criteria
    
    def _determine_validation_method(self, template: Dict[str, str]) -> ValidationMethod:
        """Determine appropriate validation method for criterion."""
        response = template['response'].lower()
        
        # UI-related responses
        if any(term in response for term in ['display', 'show', 'highlight', 'redirect']):
            return self._validation_methods['ui_test']
        
        # API-related responses
        if any(term in response for term in ['return', 'send', 'receive', 'process']):
            return self._validation_methods['api_test']
        
        # Performance-related responses
        if any(term in response for term in ['within', 'time', 'performance', 'speed']):
            return self._validation_methods['performance_test']
        
        # Security-related responses
        if any(term in response for term in ['deny', 'authenticate', 'authorize', 'security']):
            return self._validation_methods['security_test']
        
        # Default to unit test
        return self._validation_methods['unit_test']
    
    def validate_acceptance_criteria(
        self,
        criteria: List[AcceptanceCriterion]
    ) -> AcceptanceCriteriaValidationResult:
        """
        Validate a list of acceptance criteria.
        
        Args:
            criteria: List of acceptance criteria to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        result = AcceptanceCriteriaValidationResult(
            is_valid=True,
            criteria_count=len(criteria),
            testable_count=0
        )
        
        if not criteria:
            result.is_valid = False
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.ERROR,
                criterion_index=-1,
                message="No acceptance criteria provided. User stories must have acceptance criteria.",
                suggestion="Add at least 3-5 acceptance criteria covering happy path, error cases, and edge cases."
            ))
            return result
        
        # Validate each criterion
        for i, criterion in enumerate(criteria):
            self._validate_single_criterion(criterion, i, result)
        
        # Calculate testability score
        result.testability_score = self._calculate_testability_score(criteria, result)
        
        # Check overall coverage
        self._validate_coverage(criteria, result)
        
        # Generate suggestions
        self._generate_validation_suggestions(criteria, result)
        
        # Determine overall validity
        result.is_valid = not any(
            issue.severity == AcceptanceCriteriaValidationSeverity.ERROR
            for issue in result.issues
        )
        
        return result
    
    def _validate_single_criterion(
        self,
        criterion: AcceptanceCriterion,
        index: int,
        result: AcceptanceCriteriaValidationResult
    ) -> None:
        """Validate a single acceptance criterion."""
        # Validate EARS format
        ears_validation = self._ears_validator.validate_ears_statement(str(criterion.ears_format))
        
        if not ears_validation.is_valid:
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.ERROR,
                criterion_index=index,
                message=f"Invalid EARS format: {ears_validation.issues[0].message if ears_validation.issues else 'Unknown format error'}",
                suggestion="Use format: WHEN [condition] THEN [system] SHALL [response]"
            ))
        
        # Check testability
        if criterion.testable:
            result.testable_count += 1
        else:
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.WARNING,
                criterion_index=index,
                message="Criterion may not be easily testable",
                suggestion="Ensure the criterion describes observable, measurable behavior"
            ))
        
        # Validate testability patterns
        self._validate_testability_patterns(criterion, index, result)
    
    def _validate_testability_patterns(
        self,
        criterion: AcceptanceCriterion,
        index: int,
        result: AcceptanceCriteriaValidationResult
    ) -> None:
        """Validate testability patterns in criterion."""
        response = criterion.ears_format.response.lower()
        
        # Check for testable verbs
        has_testable_verb = any(
            verb in response 
            for verb in self._testability_patterns['testable_verbs']
        )
        
        if not has_testable_verb:
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.INFO,
                criterion_index=index,
                message="Consider using more specific, testable action verbs",
                suggestion="Use verbs like 'return', 'display', 'create', 'validate', etc."
            ))
        
        # Check for vague terms
        for vague_term in self._testability_patterns['vague_terms']:
            if vague_term in response:
                result.issues.append(AcceptanceCriteriaValidationIssue(
                    severity=AcceptanceCriteriaValidationSeverity.WARNING,
                    criterion_index=index,
                    message=f"Vague term '{vague_term}' found in response",
                    suggestion=f"Replace '{vague_term}' with specific, measurable criteria"
                ))
    
    def _calculate_testability_score(
        self,
        criteria: List[AcceptanceCriterion],
        result: AcceptanceCriteriaValidationResult
    ) -> float:
        """Calculate overall testability score."""
        if not criteria:
            return 0.0
        
        score = 0.0
        
        # Base score from testable criteria
        testable_ratio = result.testable_count / len(criteria)
        score += testable_ratio * 40  # Up to 40 points
        
        # Score from validation methods
        has_automated_tests = sum(
            1 for criterion in criteria
            if criterion.validation_method.method_type == "automated_test"
        )
        automated_ratio = has_automated_tests / len(criteria)
        score += automated_ratio * 30  # Up to 30 points
        
        # Score from EARS format quality
        valid_ears_count = sum(
            1 for criterion in criteria
            if self._ears_validator.validate_ears_statement(str(criterion.ears_format)).is_valid
        )
        ears_ratio = valid_ears_count / len(criteria)
        score += ears_ratio * 20  # Up to 20 points
        
        # Score from coverage (minimum criteria count)
        if len(criteria) >= 3:
            score += 10  # 10 points for having at least 3 criteria
        
        return min(score, 100.0)
    
    def _validate_coverage(
        self,
        criteria: List[AcceptanceCriterion],
        result: AcceptanceCriteriaValidationResult
    ) -> None:
        """Validate coverage of different scenarios."""
        if len(criteria) < 3:
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.WARNING,
                criterion_index=-1,
                message=f"Only {len(criteria)} acceptance criteria. Consider adding more for better coverage.",
                suggestion="Include criteria for happy path, error cases, edge cases, and boundary conditions."
            ))
        
        # Check for error handling coverage
        has_error_handling = any(
            'error' in str(criterion.ears_format).lower() or
            'invalid' in str(criterion.ears_format).lower() or
            'fail' in str(criterion.ears_format).lower()
            for criterion in criteria
        )
        
        if not has_error_handling:
            result.issues.append(AcceptanceCriteriaValidationIssue(
                severity=AcceptanceCriteriaValidationSeverity.INFO,
                criterion_index=-1,
                message="No error handling criteria found",
                suggestion="Add criteria for error cases and invalid input scenarios"
            ))
    
    def _generate_validation_suggestions(
        self,
        criteria: List[AcceptanceCriterion],
        result: AcceptanceCriteriaValidationResult
    ) -> None:
        """Generate suggestions for improving acceptance criteria."""
        # General suggestions
        result.suggestions.extend([
            "Ensure each criterion is independently testable",
            "Use specific, measurable outcomes in responses",
            "Cover both positive and negative test scenarios",
            "Include boundary conditions and edge cases"
        ])
        
        # Specific suggestions based on validation results
        if result.testability_score < 50:
            result.suggestions.append(
                "Improve testability by using more specific action verbs and measurable outcomes"
            )
        
        if result.testable_count < len(criteria) * 0.8:
            result.suggestions.append(
                "Review criteria marked as not testable and make them more specific"
            )
        
        error_count = sum(
            1 for issue in result.issues
            if issue.severity == AcceptanceCriteriaValidationSeverity.ERROR
        )
        
        if error_count > 0:
            result.suggestions.append(
                "Fix EARS format errors before proceeding with implementation"
            )
    
    def get_criteria_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available criteria templates.
        
        Args:
            category: Specific category to get templates for
            
        Returns:
            Template information
        """
        if category and category in self._criteria_templates:
            return {
                'category': category,
                'templates': self._criteria_templates[category],
                'description': f"Templates for {category} acceptance criteria"
            }
        
        return {
            'categories': list(self._criteria_templates.keys()),
            'all_templates': self._criteria_templates,
            'description': "All available acceptance criteria templates"
        }
    
    def suggest_missing_criteria(
        self,
        user_story: UserStory,
        existing_criteria: List[AcceptanceCriterion]
    ) -> List[Dict[str, str]]:
        """
        Suggest missing acceptance criteria based on user story and existing criteria.
        
        Args:
            user_story: User story to analyze
            existing_criteria: Existing acceptance criteria
            
        Returns:
            List of suggested criteria templates
        """
        suggestions = []
        
        # Analyze existing criteria coverage
        existing_text = ' '.join(str(criterion.ears_format) for criterion in existing_criteria)
        existing_lower = existing_text.lower()
        
        # Check for missing basic functionality
        if 'valid' not in existing_lower:
            suggestions.append({
                'condition': f'{user_story.role} provides valid input for {user_story.feature}',
                'system': 'the system',
                'response': 'process the request and return expected results',
                'statement_type': 'WHEN',
                'category': 'basic_functionality'
            })
        
        # Check for missing error handling
        if 'invalid' not in existing_lower and 'error' not in existing_lower:
            suggestions.append({
                'condition': f'{user_story.role} provides invalid input',
                'system': 'the system',
                'response': 'reject the input and provide clear validation feedback',
                'statement_type': 'WHEN',
                'category': 'error_handling'
            })
        
        # Check for missing security criteria (for non-public roles)
        if (user_story.role.lower() not in ['end user', 'guest', 'visitor'] and
            'authenticate' not in existing_lower and 'authorize' not in existing_lower):
            suggestions.append({
                'condition': f'{user_story.role} is not properly authenticated',
                'system': 'the system',
                'response': 'deny access and redirect to authentication',
                'statement_type': 'WHEN',
                'category': 'security'
            })
        
        return suggestions
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the acceptance criteria generator."""
        return {
            "status": "healthy",
            "criteria_templates_loaded": len(self._criteria_templates),
            "testability_patterns_loaded": len(self._testability_patterns),
            "validation_methods_loaded": len(self._validation_methods),
            "ears_validator_ready": self._ears_validator.ready(),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if acceptance criteria generator is ready for operation."""
        return (
            len(self._criteria_templates) > 0 and
            len(self._testability_patterns) > 0 and
            len(self._validation_methods) > 0 and
            self._ears_validator.ready()
        )
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "criteria_templates_count": float(len(self._criteria_templates)),
            "testability_patterns_count": float(len(self._testability_patterns)),
            "validation_methods_count": float(len(self._validation_methods))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"