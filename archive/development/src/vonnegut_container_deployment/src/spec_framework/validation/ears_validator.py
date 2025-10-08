"""
EARS Format Validation Engine - Systematic validation of EARS format requirements.

Implements automatic validation of "WHEN/IF...THEN...SHALL" format with
systematic feedback and guidance based on RM-DDD proven patterns.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import EARSStatement


logger = logging.getLogger(__name__)


class EARSStatementType(Enum):
    """Types of EARS statements."""
    WHEN = "WHEN"
    IF = "IF" 
    WHILE = "WHILE"
    WHERE = "WHERE"


class EARSValidationSeverity(Enum):
    """Severity levels for EARS validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class EARSValidationIssue:
    """Individual validation issue for EARS statement."""
    severity: EARSValidationSeverity
    message: str
    suggestion: Optional[str] = None
    position: Optional[Tuple[int, int]] = None  # (start, end) character positions


@dataclass
class EARSValidationResult:
    """Result of EARS format validation."""
    is_valid: bool
    statement_type: Optional[EARSStatementType] = None
    parsed_components: Optional[Dict[str, str]] = None
    issues: List[EARSValidationIssue] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []


class EARSFormatValidator(ReflectiveModule):
    """
    EARS Format Validation Engine.
    
    Provides systematic validation of EARS format statements with
    automatic parsing, validation, and guidance generation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the EARS format validator."""
        super().__init__()
        self._config = config or {}
        self._patterns = self._initialize_patterns()
        self._templates = self._initialize_templates()
        self._validation_rules = self._initialize_validation_rules()
        
        logger.info("EARSFormatValidator initialized with systematic patterns")
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for EARS statement parsing."""
        return {
            # Basic EARS patterns
            'when_pattern': r'^WHEN\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'if_pattern': r'^IF\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'while_pattern': r'^WHILE\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'where_pattern': r'^WHERE\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            
            # Compound patterns with AND/OR
            'compound_when': r'^WHEN\s+(.+?)\s+AND\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'compound_if': r'^IF\s+(.+?)\s+AND\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'compound_or_when': r'^WHEN\s+(.+?)\s+OR\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            'compound_or_if': r'^IF\s+(.+?)\s+OR\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+)$',
            
            # Detection patterns for common mistakes
            'missing_then': r'^(WHEN|IF|WHILE|WHERE)\s+(.+?)\s+SHALL\s+(.+)$',
            'missing_shall': r'^(WHEN|IF|WHILE|WHERE)\s+(.+?)\s+THEN\s+(.+?)$',
            'wrong_order': r'^(.+?)\s+SHALL\s+(.+?)\s+WHEN\s+(.+?)$',
            
            # Quality patterns
            'vague_condition': r'\b(something|anything|stuff|things|etc)\b',
            'vague_system': r'\b(it|system|application)\b$',
            'vague_response': r'\b(work|function|operate|do something)\b'
        }
    
    def _initialize_templates(self) -> Dict[str, List[str]]:
        """Initialize EARS statement templates for guidance."""
        return {
            'when_templates': [
                "WHEN [specific user action] THEN [specific system component] SHALL [measurable response]",
                "WHEN [specific condition occurs] THEN [named system] SHALL [specific behavior with criteria]",
                "WHEN [user provides input] THEN [system] SHALL [validate and respond with specific outcome]"
            ],
            'if_templates': [
                "IF [specific precondition] THEN [system component] SHALL [conditional behavior]",
                "IF [error condition detected] THEN [system] SHALL [specific error handling response]",
                "IF [configuration setting] THEN [system] SHALL [adapted behavior]"
            ],
            'while_templates': [
                "WHILE [ongoing condition] THEN [system] SHALL [continuous behavior]",
                "WHILE [process is running] THEN [system] SHALL [monitoring behavior]"
            ],
            'where_templates': [
                "WHERE [context or environment] THEN [system] SHALL [context-specific behavior]"
            ]
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for EARS components."""
        return {
            'condition_rules': {
                'min_length': 5,
                'max_length': 200,
                'required_elements': ['specific trigger or state'],
                'avoid_words': ['something', 'anything', 'stuff', 'things'],
                'should_contain': ['specific', 'measurable', 'observable']
            },
            'system_rules': {
                'min_length': 3,
                'max_length': 100,
                'required_elements': ['specific system or component name'],
                'avoid_words': ['it', 'the system', 'application'],
                'should_be_specific': True
            },
            'response_rules': {
                'min_length': 5,
                'max_length': 300,
                'required_elements': ['specific action', 'measurable outcome'],
                'avoid_words': ['work', 'function', 'operate', 'do something'],
                'should_contain': ['specific', 'measurable', 'testable']
            }
        }
    
    def validate_ears_statement(self, statement: str) -> EARSValidationResult:
        """
        Validate a complete EARS statement.
        
        Args:
            statement: EARS statement string to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        statement = statement.strip()
        result = EARSValidationResult(is_valid=False)
        
        # Try to parse the statement
        parsed = self._parse_ears_statement(statement)
        
        if parsed:
            result.statement_type = parsed['type']
            result.parsed_components = parsed['components']
            
            # Validate each component
            self._validate_condition(parsed['components']['condition'], result)
            self._validate_system(parsed['components']['system'], result)
            self._validate_response(parsed['components']['response'], result)
            
            # Check overall structure
            self._validate_structure(statement, result)
            
            # Determine if valid (no errors)
            result.is_valid = not any(
                issue.severity == EARSValidationSeverity.ERROR 
                for issue in result.issues
            )
        else:
            # Failed to parse - identify the issue
            self._diagnose_parsing_failure(statement, result)
        
        # Generate suggestions
        self._generate_suggestions(statement, result)
        
        return result
    
    def _parse_ears_statement(self, statement: str) -> Optional[Dict[str, Any]]:
        """
        Parse EARS statement into components.
        
        Args:
            statement: Statement to parse
            
        Returns:
            Parsed components or None if parsing fails
        """
        # Try each pattern using original case for matching but preserve original text
        for pattern_name, pattern in self._patterns.items():
            if pattern_name.endswith('_pattern'):
                match = re.match(pattern, statement, re.IGNORECASE | re.DOTALL)
                if match:
                    groups = match.groups()
                    
                    # Determine statement type
                    if pattern_name.startswith('when'):
                        stmt_type = EARSStatementType.WHEN
                    elif pattern_name.startswith('if'):
                        stmt_type = EARSStatementType.IF
                    elif pattern_name.startswith('while'):
                        stmt_type = EARSStatementType.WHILE
                    elif pattern_name.startswith('where'):
                        stmt_type = EARSStatementType.WHERE
                    else:
                        continue
                    
                    # Handle compound statements
                    if 'compound' in pattern_name:
                        if len(groups) == 4:
                            condition = f"{groups[0]} AND {groups[1]}"
                            system = groups[2]
                            response = groups[3]
                        else:
                            continue
                    else:
                        if len(groups) == 3:
                            condition = groups[0]
                            system = groups[1]
                            response = groups[2]
                        else:
                            continue
                    
                    return {
                        'type': stmt_type,
                        'components': {
                            'condition': condition.strip(),
                            'system': system.strip(),
                            'response': response.strip()
                        }
                    }
        
        return None
    
    def _validate_condition(self, condition: str, result: EARSValidationResult) -> None:
        """Validate the condition component of EARS statement."""
        rules = self._validation_rules['condition_rules']
        
        # Length validation
        if len(condition) < rules['min_length']:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message=f"Condition too short ({len(condition)} chars). Should be at least {rules['min_length']} characters.",
                suggestion="Provide more specific details about when this requirement applies."
            ))
        
        if len(condition) > rules['max_length']:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.WARNING,
                message=f"Condition very long ({len(condition)} chars). Consider breaking into multiple requirements.",
                suggestion="Split complex conditions into separate, simpler requirements."
            ))
        
        # Avoid vague words
        for avoid_word in rules['avoid_words']:
            if re.search(r'\b' + re.escape(avoid_word) + r'\b', condition, re.IGNORECASE):
                result.issues.append(EARSValidationIssue(
                    severity=EARSValidationSeverity.WARNING,
                    message=f"Vague term '{avoid_word}' found in condition.",
                    suggestion=f"Replace '{avoid_word}' with specific, measurable criteria."
                ))
        
        # Check for specificity
        if re.search(self._patterns['vague_condition'], condition, re.IGNORECASE):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.WARNING,
                message="Condition contains vague terms that may be hard to test.",
                suggestion="Use specific, observable, and measurable conditions."
            ))
    
    def _validate_system(self, system: str, result: EARSValidationResult) -> None:
        """Validate the system component of EARS statement."""
        rules = self._validation_rules['system_rules']
        
        # Length validation
        if len(system) < rules['min_length']:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message=f"System component too short ({len(system)} chars).",
                suggestion="Specify the exact system, component, or service responsible."
            ))
        
        # Avoid vague system references
        for avoid_word in rules['avoid_words']:
            if system.lower() == avoid_word.lower():
                result.issues.append(EARSValidationIssue(
                    severity=EARSValidationSeverity.WARNING,
                    message=f"Vague system reference '{avoid_word}'.",
                    suggestion="Name the specific system, service, or component responsible."
                ))
        
        # Check for vague system patterns
        if re.search(self._patterns['vague_system'], system, re.IGNORECASE):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.WARNING,
                message="System component is too generic.",
                suggestion="Specify the exact system component, service, or module."
            ))
    
    def _validate_response(self, response: str, result: EARSValidationResult) -> None:
        """Validate the response component of EARS statement."""
        rules = self._validation_rules['response_rules']
        
        # Length validation
        if len(response) < rules['min_length']:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message=f"Response too short ({len(response)} chars).",
                suggestion="Describe the specific, measurable behavior or outcome."
            ))
        
        # Avoid vague responses
        for avoid_word in rules['avoid_words']:
            if re.search(r'\b' + re.escape(avoid_word) + r'\b', response, re.IGNORECASE):
                result.issues.append(EARSValidationIssue(
                    severity=EARSValidationSeverity.WARNING,
                    message=f"Vague term '{avoid_word}' found in response.",
                    suggestion=f"Replace '{avoid_word}' with specific, testable behavior."
                ))
        
        # Check for vague response patterns
        if re.search(self._patterns['vague_response'], response, re.IGNORECASE):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.WARNING,
                message="Response contains vague terms that may be hard to test.",
                suggestion="Specify exact behavior, outputs, or measurable outcomes."
            ))
        
        # Check for testability indicators
        testability_indicators = [
            'return', 'display', 'send', 'create', 'update', 'delete',
            'validate', 'reject', 'accept', 'notify', 'log', 'store'
        ]
        
        has_testable_action = any(
            indicator in response.lower() 
            for indicator in testability_indicators
        )
        
        if not has_testable_action:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.INFO,
                message="Response may not be easily testable.",
                suggestion="Include specific actions like 'return', 'display', 'validate', etc."
            ))
    
    def _validate_structure(self, statement: str, result: EARSValidationResult) -> None:
        """Validate overall EARS statement structure."""
        statement_upper = statement.upper()
        
        # Check for proper EARS keywords
        if 'THEN' not in statement_upper:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'THEN' keyword in EARS statement.",
                suggestion="EARS format requires: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        if 'SHALL' not in statement_upper:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'SHALL' keyword in EARS statement.",
                suggestion="EARS format requires: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        # Check keyword order
        then_pos = statement_upper.find('THEN')
        shall_pos = statement_upper.find('SHALL')
        
        if then_pos > 0 and shall_pos > 0 and then_pos > shall_pos:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Keywords in wrong order. 'THEN' should come before 'SHALL'.",
                suggestion="Correct order: [WHEN/IF] condition THEN system SHALL response"
            ))
    
    def _diagnose_parsing_failure(self, statement: str, result: EARSValidationResult) -> None:
        """Diagnose why EARS statement parsing failed."""
        statement_upper = statement.upper()
        
        # Check for missing keywords at the beginning
        trigger_keywords = ['WHEN', 'IF', 'WHILE', 'WHERE']
        has_trigger_at_start = any(statement_upper.startswith(kw) for kw in trigger_keywords)
        
        if not has_trigger_at_start:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing trigger keyword. EARS statements must start with WHEN, IF, WHILE, or WHERE.",
                suggestion="Start with: WHEN [condition] THEN [system] SHALL [response]"
            ))
        
        # Check for missing THEN
        if 'THEN' not in statement_upper:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'THEN' keyword between condition and system.",
                suggestion="Format: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        # Check for missing SHALL
        if 'SHALL' not in statement_upper:
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'SHALL' keyword before response.",
                suggestion="Format: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        # Check for common patterns that indicate wrong format
        if re.search(self._patterns['missing_then'], statement_upper):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'THEN' keyword between condition and system.",
                suggestion="Format: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        if re.search(self._patterns['missing_shall'], statement_upper):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Missing 'SHALL' keyword before response.",
                suggestion="Format: [WHEN/IF] condition THEN system SHALL response"
            ))
        
        if re.search(self._patterns['wrong_order'], statement_upper):
            result.issues.append(EARSValidationIssue(
                severity=EARSValidationSeverity.ERROR,
                message="Keywords in wrong order.",
                suggestion="Correct order: [WHEN/IF] condition THEN system SHALL response"
            ))
    
    def _generate_suggestions(self, statement: str, result: EARSValidationResult) -> None:
        """Generate improvement suggestions for EARS statement."""
        if result.statement_type:
            # Get appropriate templates
            template_key = f"{result.statement_type.value.lower()}_templates"
            if template_key in self._templates:
                result.suggestions.extend(self._templates[template_key])
        else:
            # Provide basic templates
            result.suggestions.extend([
                "WHEN [user performs specific action] THEN [named system] SHALL [specific measurable response]",
                "IF [specific condition is met] THEN [system component] SHALL [defined behavior]",
                "WHILE [ongoing condition exists] THEN [system] SHALL [continuous behavior]"
            ])
        
        # Add specific suggestions based on issues
        error_count = sum(1 for issue in result.issues if issue.severity == EARSValidationSeverity.ERROR)
        if error_count > 0:
            result.suggestions.append(
                "Focus on fixing structural errors first, then improve specificity and testability."
            )
    
    def create_ears_statement(
        self,
        condition: str,
        system: str,
        response: str,
        statement_type: str = "WHEN"
    ) -> EARSStatement:
        """
        Create and validate an EARS statement.
        
        Args:
            condition: Condition part
            system: System part
            response: Response part
            statement_type: Type of statement (WHEN, IF, WHILE, WHERE)
            
        Returns:
            EARSStatement object
        """
        ears_statement = EARSStatement(
            condition=condition,
            system=system,
            response=response,
            statement_type=statement_type.upper()
        )
        
        # Validate the created statement
        validation_result = self.validate_ears_statement(str(ears_statement))
        
        if not validation_result.is_valid:
            logger.warning(f"Created EARS statement has validation issues: {validation_result.issues}")
        
        return ears_statement
    
    def get_validation_guidance(self, statement_type: str = "WHEN") -> Dict[str, Any]:
        """
        Get validation guidance for creating EARS statements.
        
        Args:
            statement_type: Type of EARS statement
            
        Returns:
            Guidance information
        """
        template_key = f"{statement_type.lower()}_templates"
        
        return {
            'statement_type': statement_type,
            'format': f"{statement_type} [condition] THEN [system] SHALL [response]",
            'templates': self._templates.get(template_key, []),
            'condition_guidelines': [
                "Be specific and observable",
                "Avoid vague terms like 'something', 'anything'",
                "Make it testable and measurable",
                "Keep it focused on a single trigger"
            ],
            'system_guidelines': [
                "Name the specific system or component",
                "Avoid generic terms like 'the system', 'it'",
                "Be precise about what part is responsible"
            ],
            'response_guidelines': [
                "Describe specific, measurable behavior",
                "Use action verbs like 'return', 'display', 'validate'",
                "Avoid vague terms like 'work', 'function'",
                "Make it testable and verifiable"
            ]
        }
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the EARS validator."""
        return {
            "status": "healthy",
            "patterns_loaded": len(self._patterns),
            "templates_loaded": len(self._templates),
            "validation_rules_loaded": len(self._validation_rules),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if EARS validator is ready for operation."""
        return (
            len(self._patterns) > 0 and
            len(self._templates) > 0 and
            len(self._validation_rules) > 0
        )
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "patterns_count": float(len(self._patterns)),
            "templates_count": float(len(self._templates)),
            "validation_rules_count": float(len(self._validation_rules))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        if not self.ready():
            return "initializing"
        else:
            return "ready"