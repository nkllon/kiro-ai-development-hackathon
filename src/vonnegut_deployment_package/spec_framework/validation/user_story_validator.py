"""
User Story Template System - Systematic validation and management of user stories.

Implements "As a [role], I want [feature], so that [benefit]" validation with
role library and benefit validation based on RM-DDD patterns.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import UserStory


logger = logging.getLogger(__name__)


class UserStoryValidationSeverity(Enum):
    """Severity levels for user story validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class UserStoryValidationIssue:
    """Individual validation issue for user story."""
    severity: UserStoryValidationSeverity
    component: str  # "role", "feature", "benefit", "structure"
    message: str
    suggestion: Optional[str] = None
    position: Optional[Tuple[int, int]] = None  # (start, end) character positions


@dataclass
class UserStoryValidationResult:
    """Result of user story validation."""
    is_valid: bool
    parsed_components: Optional[Dict[str, str]] = None
    issues: List[UserStoryValidationIssue] = None
    suggestions: List[str] = None
    business_value_score: float = 0.0  # 0-100 score for business value clarity
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []


class UserStoryTemplateSystem(ReflectiveModule):
    """
    User Story Template System.
    
    Provides systematic validation of user stories with role library,
    benefit validation, and completeness checking based on RM-DDD patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the user story template system."""
        super().__init__()
        self._config = config or {}
        self._role_library = self._initialize_role_library()
        self._role_patterns = self._initialize_role_patterns()
        self._benefit_patterns = self._initialize_benefit_patterns()
        self._feature_patterns = self._initialize_feature_patterns()
        self._validation_rules = self._initialize_validation_rules()
        
        logger.info("UserStoryTemplateSystem initialized with systematic validation")
    
    def _initialize_role_library(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive role library based on RM-DDD patterns."""
        return {
            # Technical roles
            "developer": {
                "category": "technical",
                "description": "Software developer implementing features",
                "typical_needs": ["clear requirements", "technical specifications", "development tools"],
                "common_benefits": ["faster development", "reduced bugs", "better code quality"]
            },
            "system architect": {
                "category": "technical", 
                "description": "System architect designing solutions",
                "typical_needs": ["architectural patterns", "integration requirements", "scalability needs"],
                "common_benefits": ["better system design", "improved maintainability", "reduced technical debt"]
            },
            "devops engineer": {
                "category": "technical",
                "description": "DevOps engineer managing deployment and operations",
                "typical_needs": ["deployment automation", "monitoring", "infrastructure management"],
                "common_benefits": ["faster deployments", "improved reliability", "reduced operational overhead"]
            },
            "quality assurance engineer": {
                "category": "technical",
                "description": "QA engineer ensuring quality",
                "typical_needs": ["test automation", "quality metrics", "validation tools"],
                "common_benefits": ["better quality", "faster testing", "reduced defects"]
            },
            
            # Management roles
            "project manager": {
                "category": "management",
                "description": "Project manager coordinating development",
                "typical_needs": ["progress tracking", "resource planning", "risk management"],
                "common_benefits": ["better visibility", "improved coordination", "reduced risks"]
            },
            "team lead": {
                "category": "management",
                "description": "Team lead managing development team",
                "typical_needs": ["team coordination", "technical guidance", "progress monitoring"],
                "common_benefits": ["better team productivity", "improved communication", "reduced blockers"]
            },
            "product owner": {
                "category": "management",
                "description": "Product owner defining requirements",
                "typical_needs": ["feature prioritization", "user feedback", "business alignment"],
                "common_benefits": ["better product-market fit", "improved user satisfaction", "increased business value"]
            },
            
            # Business roles
            "business analyst": {
                "category": "business",
                "description": "Business analyst defining requirements",
                "typical_needs": ["requirements analysis", "process modeling", "stakeholder communication"],
                "common_benefits": ["clearer requirements", "better process efficiency", "improved stakeholder alignment"]
            },
            "compliance officer": {
                "category": "business",
                "description": "Compliance officer ensuring regulatory compliance",
                "typical_needs": ["audit trails", "compliance reporting", "risk assessment"],
                "common_benefits": ["regulatory compliance", "reduced audit risk", "improved governance"]
            },
            
            # User roles
            "end user": {
                "category": "user",
                "description": "End user of the system",
                "typical_needs": ["intuitive interface", "reliable functionality", "good performance"],
                "common_benefits": ["improved productivity", "better user experience", "reduced frustration"]
            },
            "administrator": {
                "category": "user",
                "description": "System administrator managing the system",
                "typical_needs": ["management tools", "monitoring capabilities", "configuration options"],
                "common_benefits": ["easier administration", "better system control", "reduced maintenance effort"]
            },
            "power user": {
                "category": "user",
                "description": "Advanced user with specialized needs",
                "typical_needs": ["advanced features", "customization options", "automation capabilities"],
                "common_benefits": ["increased efficiency", "better workflow integration", "enhanced capabilities"]
            },
            
            # Specialized roles
            "security architect": {
                "category": "specialized",
                "description": "Security architect ensuring system security",
                "typical_needs": ["security patterns", "threat modeling", "compliance validation"],
                "common_benefits": ["improved security posture", "reduced security risks", "better compliance"]
            },
            "performance engineer": {
                "category": "specialized",
                "description": "Performance engineer optimizing system performance",
                "typical_needs": ["performance metrics", "optimization tools", "scalability analysis"],
                "common_benefits": ["better performance", "improved scalability", "reduced resource usage"]
            },
            "technical writer": {
                "category": "specialized",
                "description": "Technical writer creating documentation",
                "typical_needs": ["documentation tools", "content management", "collaboration features"],
                "common_benefits": ["better documentation quality", "improved user adoption", "reduced support burden"]
            }
        }
    
    def _initialize_role_patterns(self) -> Dict[str, str]:
        """Initialize patterns for role validation."""
        return {
            'generic_role': r'\b(user|person|someone|anybody|everyone)\b',
            'vague_role': r'\b(stakeholder|member|individual)\b',
            'specific_role': r'\b(developer|architect|manager|analyst|engineer|officer|administrator)\b'
        }
    
    def _initialize_benefit_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for benefit validation."""
        return {
            'business_value_indicators': [
                'increased', 'improved', 'reduced', 'faster', 'better', 'enhanced',
                'streamlined', 'optimized', 'automated', 'simplified', 'accelerated'
            ],
            'measurable_outcomes': [
                'productivity', 'efficiency', 'quality', 'performance', 'reliability',
                'security', 'compliance', 'satisfaction', 'revenue', 'cost', 'time',
                'accuracy', 'consistency', 'visibility', 'control'
            ],
            'vague_benefits': [
                'things work better', 'it is good', 'system is improved', 'users are happy',
                'everything is easier', 'stuff gets done', 'it helps'
            ]
        }
    
    def _initialize_feature_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for feature validation."""
        return {
            'action_verbs': [
                'create', 'update', 'delete', 'view', 'search', 'filter', 'sort',
                'export', 'import', 'configure', 'manage', 'monitor', 'analyze',
                'validate', 'approve', 'reject', 'submit', 'process', 'generate'
            ],
            'vague_features': [
                'do something', 'use the system', 'work with data', 'manage things',
                'handle stuff', 'process items', 'deal with information'
            ]
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for user story components."""
        return {
            'role_rules': {
                'min_length': 3,
                'max_length': 50,
                'must_be_specific': True,
                'avoid_generic_terms': True,
                'should_be_in_library': True
            },
            'feature_rules': {
                'min_length': 10,
                'max_length': 200,
                'should_contain_action': True,
                'should_be_specific': True,
                'avoid_vague_terms': True
            },
            'benefit_rules': {
                'min_length': 10,
                'max_length': 300,
                'should_show_business_value': True,
                'should_be_measurable': True,
                'avoid_vague_terms': True
            }
        }
    
    def validate_user_story(self, user_story_text: str) -> UserStoryValidationResult:
        """
        Validate a complete user story.
        
        Args:
            user_story_text: User story text to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        result = UserStoryValidationResult(is_valid=False)
        
        # Parse the user story
        parsed = self._parse_user_story(user_story_text)
        
        if parsed:
            result.parsed_components = parsed
            
            # Validate each component
            self._validate_role(parsed['role'], result)
            self._validate_feature(parsed['feature'], result)
            self._validate_benefit(parsed['benefit'], result)
            
            # Calculate business value score
            result.business_value_score = self._calculate_business_value_score(parsed)
            
            # Check overall structure
            self._validate_structure(user_story_text, result)
            
            # Determine if valid (no errors)
            result.is_valid = not any(
                issue.severity == UserStoryValidationSeverity.ERROR 
                for issue in result.issues
            )
        else:
            # Failed to parse - identify the issue
            self._diagnose_parsing_failure(user_story_text, result)
        
        # Generate suggestions
        self._generate_suggestions(user_story_text, result)
        
        return result
    
    def _parse_user_story(self, user_story_text: str) -> Optional[Dict[str, str]]:
        """
        Parse user story into components.
        
        Args:
            user_story_text: User story text to parse
            
        Returns:
            Parsed components or None if parsing fails
        """
        # Standard user story pattern - handle "As a/an" properly
        pattern = r'(?i)^as\s+(?:an?\s+)?(.+?),\s*i\s+want\s+(?:to\s+)?(.+?),\s*so\s+that\s+(.+)$'
        
        match = re.match(pattern, user_story_text.strip(), re.IGNORECASE | re.DOTALL)
        
        if match:
            role = match.group(1).strip()
            feature = match.group(2).strip()
            benefit = match.group(3).strip()
            
            # Clean up role - remove leading "a" or "an" if captured
            role = re.sub(r'^(?:a\s+|an\s+)', '', role, flags=re.IGNORECASE).strip()
            
            return {
                'role': role,
                'feature': feature,
                'benefit': benefit
            }
        
        # Try alternative patterns
        alt_patterns = [
            r'(?i)^as\s+(?:an?\s+)?(.+?),\s*i\s+need\s+(?:to\s+)?(.+?),\s*so\s+that\s+(.+)$',
            r'(?i)^as\s+(?:an?\s+)?(.+?),\s*i\s+would\s+like\s+(?:to\s+)?(.+?),\s*so\s+that\s+(.+)$'
        ]
        
        for alt_pattern in alt_patterns:
            match = re.match(alt_pattern, user_story_text.strip(), re.IGNORECASE | re.DOTALL)
            if match:
                role = match.group(1).strip()
                feature = match.group(2).strip()
                benefit = match.group(3).strip()
                
                # Clean up role - remove leading "a" or "an" if captured
                role = re.sub(r'^(?:a\s+|an\s+)', '', role, flags=re.IGNORECASE).strip()
                
                return {
                    'role': role,
                    'feature': feature,
                    'benefit': benefit
                }
        
        return None
    
    def _validate_role(self, role: str, result: UserStoryValidationResult) -> None:
        """Validate the role component of user story."""
        rules = self._validation_rules['role_rules']
        
        # Length validation
        if len(role) < rules['min_length']:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="role",
                message=f"Role too short ({len(role)} chars). Should be at least {rules['min_length']} characters.",
                suggestion="Provide a specific role like 'developer', 'project manager', or 'end user'."
            ))
        
        if len(role) > rules['max_length']:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="role",
                message=f"Role very long ({len(role)} chars). Consider simplifying.",
                suggestion="Use a concise, specific role description."
            ))
        
        # Check if role is in library
        role_lower = role.lower()
        if role_lower not in self._role_library:
            # Check for partial matches
            partial_matches = [
                lib_role for lib_role in self._role_library.keys()
                if lib_role in role_lower or role_lower in lib_role
            ]
            
            if partial_matches:
                result.issues.append(UserStoryValidationIssue(
                    severity=UserStoryValidationSeverity.INFO,
                    component="role",
                    message=f"Role '{role}' not in standard library. Did you mean: {', '.join(partial_matches)}?",
                    suggestion=f"Consider using standard role: {partial_matches[0]}"
                ))
            else:
                result.issues.append(UserStoryValidationIssue(
                    severity=UserStoryValidationSeverity.WARNING,
                    component="role",
                    message=f"Role '{role}' not in standard library.",
                    suggestion="Consider using a standard role from the library for consistency."
                ))
        
        # Check for generic roles
        if re.search(self._role_patterns['generic_role'], role, re.IGNORECASE):
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="role",
                message="Generic role detected. Be more specific about who needs this feature.",
                suggestion="Replace generic terms with specific roles like 'developer', 'administrator', etc."
            ))
        
        # Check for vague roles
        if re.search(self._role_patterns['vague_role'], role, re.IGNORECASE):
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="role",
                message="Vague role detected. Be more specific about the user type.",
                suggestion="Use specific roles that clearly identify the user's context and needs."
            ))
    
    def _validate_feature(self, feature: str, result: UserStoryValidationResult) -> None:
        """Validate the feature component of user story."""
        rules = self._validation_rules['feature_rules']
        
        # Length validation
        if len(feature) < rules['min_length']:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="feature",
                message=f"Feature description too short ({len(feature)} chars).",
                suggestion="Provide a clear, specific description of what the user wants to do."
            ))
        
        if len(feature) > rules['max_length']:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="feature",
                message=f"Feature description very long ({len(feature)} chars). Consider breaking into multiple stories.",
                suggestion="Split complex features into smaller, focused user stories."
            ))
        
        # Check for action verbs
        has_action_verb = any(
            verb in feature.lower() 
            for verb in self._feature_patterns['action_verbs']
        )
        
        if not has_action_verb:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="feature",
                message="Feature should describe a specific action or capability.",
                suggestion="Include action verbs like 'create', 'view', 'update', 'delete', 'search', etc."
            ))
        
        # Check for vague features
        for vague_feature in self._feature_patterns['vague_features']:
            if vague_feature in feature.lower():
                result.issues.append(UserStoryValidationIssue(
                    severity=UserStoryValidationSeverity.WARNING,
                    component="feature",
                    message=f"Vague feature description: '{vague_feature}'",
                    suggestion="Be specific about what the user wants to accomplish."
                ))
    
    def _validate_benefit(self, benefit: str, result: UserStoryValidationResult) -> None:
        """Validate the benefit component of user story."""
        rules = self._validation_rules['benefit_rules']
        
        # Length validation
        if len(benefit) < rules['min_length']:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="benefit",
                message=f"Benefit description too short ({len(benefit)} chars).",
                suggestion="Explain the business value and why this feature matters."
            ))
        
        # Check for business value indicators
        has_value_indicator = any(
            indicator in benefit.lower() 
            for indicator in self._benefit_patterns['business_value_indicators']
        )
        
        if not has_value_indicator:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.WARNING,
                component="benefit",
                message="Benefit should clearly indicate business value.",
                suggestion="Use words like 'increased', 'improved', 'reduced', 'faster', 'better' to show value."
            ))
        
        # Check for measurable outcomes
        has_measurable_outcome = any(
            outcome in benefit.lower() 
            for outcome in self._benefit_patterns['measurable_outcomes']
        )
        
        if not has_measurable_outcome:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.INFO,
                component="benefit",
                message="Consider including measurable outcomes in the benefit.",
                suggestion="Reference specific outcomes like 'productivity', 'efficiency', 'quality', etc."
            ))
        
        # Check for vague benefits
        for vague_benefit in self._benefit_patterns['vague_benefits']:
            if vague_benefit in benefit.lower():
                result.issues.append(UserStoryValidationIssue(
                    severity=UserStoryValidationSeverity.WARNING,
                    component="benefit",
                    message=f"Vague benefit description: '{vague_benefit}'",
                    suggestion="Be specific about the business value and measurable outcomes."
                ))
    
    def _calculate_business_value_score(self, parsed: Dict[str, str]) -> float:
        """Calculate business value score for the user story."""
        score = 0.0
        
        # Role specificity (0-30 points)
        role = parsed['role'].lower()
        if role in self._role_library:
            score += 30.0
        elif any(lib_role in role for lib_role in self._role_library.keys()):
            score += 20.0
        elif not re.search(self._role_patterns['generic_role'], role):
            score += 15.0
        else:
            score += 5.0  # Even generic roles get some points
        
        # Feature clarity (0-35 points)
        feature = parsed['feature'].lower()
        action_verb_count = sum(1 for verb in self._feature_patterns['action_verbs'] if verb in feature)
        score += min(action_verb_count * 8, 20)  # Up to 20 points for action verbs
        
        if len(feature) >= 15:  # Reasonable detail
            score += 10
        
        if len(feature) >= 30:  # Good detail
            score += 5
        
        # Benefit value (0-35 points)
        benefit = parsed['benefit'].lower()
        value_indicator_count = sum(1 for indicator in self._benefit_patterns['business_value_indicators'] if indicator in benefit)
        score += min(value_indicator_count * 8, 20)  # Up to 20 points for value indicators
        
        measurable_outcome_count = sum(1 for outcome in self._benefit_patterns['measurable_outcomes'] if outcome in benefit)
        score += min(measurable_outcome_count * 5, 15)  # Up to 15 points for measurable outcomes
        
        # Bonus points for well-structured stories
        if len(benefit) >= 20:  # Detailed benefit
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    def _validate_structure(self, user_story_text: str, result: UserStoryValidationResult) -> None:
        """Validate overall user story structure."""
        text_lower = user_story_text.lower()
        
        # Check for proper format keywords
        if not text_lower.startswith('as '):
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story should start with 'As a' or 'As an'.",
                suggestion="Format: As a [role], I want [feature], so that [benefit]"
            ))
        
        if ' i want ' not in text_lower and ' i need ' not in text_lower and ' i would like ' not in text_lower:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story should include 'I want', 'I need', or 'I would like'.",
                suggestion="Format: As a [role], I want [feature], so that [benefit]"
            ))
        
        if ' so that ' not in text_lower and ' so i can ' not in text_lower:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story should include 'so that' or 'so I can' to explain the benefit.",
                suggestion="Format: As a [role], I want [feature], so that [benefit]"
            ))
    
    def _diagnose_parsing_failure(self, user_story_text: str, result: UserStoryValidationResult) -> None:
        """Diagnose why user story parsing failed."""
        text_lower = user_story_text.lower()
        
        # Check for missing components
        if not text_lower.startswith('as '):
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story must start with 'As a' or 'As an'.",
                suggestion="Start with: As a [role], I want [feature], so that [benefit]"
            ))
        
        if 'i want' not in text_lower and 'i need' not in text_lower:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story must include 'I want' or 'I need'.",
                suggestion="Include: I want [specific feature or capability]"
            ))
        
        if 'so that' not in text_lower and 'so i can' not in text_lower:
            result.issues.append(UserStoryValidationIssue(
                severity=UserStoryValidationSeverity.ERROR,
                component="structure",
                message="User story must include 'so that' or 'so I can'.",
                suggestion="Include: so that [business benefit or value]"
            ))
    
    def _generate_suggestions(self, user_story_text: str, result: UserStoryValidationResult) -> None:
        """Generate improvement suggestions for user story."""
        # Provide templates based on validation results
        if result.parsed_components:
            role = result.parsed_components.get('role', '').lower()
            
            # Suggest role-specific templates
            if role in self._role_library:
                role_info = self._role_library[role]
                result.suggestions.append(
                    f"For {role}: Consider features related to {', '.join(role_info['typical_needs'][:2])}"
                )
                result.suggestions.append(
                    f"For {role}: Benefits often include {', '.join(role_info['common_benefits'][:2])}"
                )
        
        # General templates
        result.suggestions.extend([
            "As a [specific role], I want to [specific action with object], so that I can [measurable benefit]",
            "As a [role], I want [feature with clear scope], so that [business value with impact]",
            "Example: As a developer, I want to view automated test results in the IDE, so that I can quickly identify and fix failing tests"
        ])
        
        # Specific suggestions based on issues
        error_count = sum(1 for issue in result.issues if issue.severity == UserStoryValidationSeverity.ERROR)
        if error_count > 0:
            result.suggestions.append(
                "Focus on fixing structural errors first, then improve specificity and business value."
            )
    
    def create_user_story(
        self,
        role: str,
        feature: str,
        benefit: str
    ) -> UserStory:
        """
        Create and validate a user story.
        
        Args:
            role: User role
            feature: Feature description
            benefit: Benefit description
            
        Returns:
            UserStory object
        """
        user_story = UserStory(
            role=role,
            feature=feature,
            benefit=benefit
        )
        
        # Validate the created user story
        validation_result = self.validate_user_story(str(user_story))
        
        if not validation_result.is_valid:
            logger.warning(f"Created user story has validation issues: {validation_result.issues}")
        
        return user_story
    
    def get_role_suggestions(self, partial_role: str = "") -> List[Dict[str, Any]]:
        """
        Get role suggestions from the library.
        
        Args:
            partial_role: Partial role name for filtering
            
        Returns:
            List of matching roles with details
        """
        if not partial_role:
            return [
                {
                    'role': role,
                    'category': info['category'],
                    'description': info['description']
                }
                for role, info in self._role_library.items()
            ]
        
        partial_lower = partial_role.lower()
        matches = []
        
        for role, info in self._role_library.items():
            if (partial_lower in role.lower() or 
                partial_lower in info['description'].lower() or
                any(partial_lower in need.lower() for need in info['typical_needs'])):
                matches.append({
                    'role': role,
                    'category': info['category'],
                    'description': info['description'],
                    'typical_needs': info['typical_needs'],
                    'common_benefits': info['common_benefits']
                })
        
        return matches
    
    def get_template_guidance(self, role: str = "") -> Dict[str, Any]:
        """
        Get template guidance for creating user stories.
        
        Args:
            role: Specific role for targeted guidance
            
        Returns:
            Guidance information
        """
        guidance = {
            'format': "As a [role], I want [feature], so that [benefit]",
            'components': {
                'role': {
                    'description': "Specific user type who needs the feature",
                    'guidelines': [
                        "Be specific about the user type",
                        "Use roles from the standard library when possible",
                        "Avoid generic terms like 'user' or 'person'",
                        "Consider the user's context and expertise level"
                    ]
                },
                'feature': {
                    'description': "What the user wants to do or accomplish",
                    'guidelines': [
                        "Use action verbs to describe specific capabilities",
                        "Be clear about the scope and boundaries",
                        "Focus on a single, coherent feature",
                        "Make it testable and implementable"
                    ]
                },
                'benefit': {
                    'description': "Why the feature provides business value",
                    'guidelines': [
                        "Explain the business value clearly",
                        "Use measurable outcomes when possible",
                        "Connect to user goals and organizational objectives",
                        "Avoid vague statements like 'it will be better'"
                    ]
                }
            },
            'examples': [
                "As a developer, I want to run automated tests from the IDE, so that I can quickly validate my code changes",
                "As a project manager, I want to view real-time progress dashboards, so that I can identify blockers early",
                "As an end user, I want to export my data in multiple formats, so that I can use it in other tools"
            ]
        }
        
        # Add role-specific guidance
        if role and role.lower() in self._role_library:
            role_info = self._role_library[role.lower()]
            guidance['role_specific'] = {
                'typical_needs': role_info['typical_needs'],
                'common_benefits': role_info['common_benefits'],
                'category': role_info['category'],
                'description': role_info['description']
            }
        
        return guidance
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the user story template system."""
        return {
            "status": "healthy",
            "role_library_size": len(self._role_library),
            "role_patterns_loaded": len(self._role_patterns),
            "benefit_patterns_loaded": len(self._benefit_patterns),
            "feature_patterns_loaded": len(self._feature_patterns),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if user story template system is ready for operation."""
        return (
            len(self._role_library) > 0 and
            len(self._role_patterns) > 0 and
            len(self._benefit_patterns) > 0 and
            len(self._feature_patterns) > 0
        )
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "role_library_size": float(len(self._role_library)),
            "role_patterns_count": float(len(self._role_patterns)),
            "benefit_patterns_count": float(len(self._benefit_patterns)),
            "feature_patterns_count": float(len(self._feature_patterns))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"