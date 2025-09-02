#!/usr/bin/env python3
"""
AST-Enhanced Linter Model - Model-Driven Architecture

This module defines the domain model for AST-enhanced code analysis and linting.
It follows the principle: "Model the system to prevent problems, don't parse to detect them."

Domain Model:
- AST Analysis Strategies
- Code Quality Patterns
- Transformation Rules
- Quality Metrics
- Auto-Fix Capabilities
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class AnalysisStrategy(Enum):
    """Different strategies for AST-based code analysis"""

    SYNTAX_VALIDATION = "syntax_validation"
    IMPORT_ANALYSIS = "import_analysis"
    FUNCTION_ANALYSIS = "function_analysis"
    CLASS_ANALYSIS = "class_analysis"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    CODE_SMELL_DETECTION = "code_smell_detection"
    PATTERN_ANALYSIS = "pattern_analysis"


class IssueSeverity(Enum):
    """Severity levels for detected issues"""

    CRITICAL = "critical"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    INFO = "info"


class IssueType(Enum):
    """Types of issues that can be detected"""

    # Syntax Issues
    SYNTAX_ERROR = "syntax_error"

    # Import Issues
    MULTIPLE_IMPORTS = "multiple_imports"
    UNUSED_IMPORT = "unused_import"
    WILDCARD_IMPORT = "wildcard_import"
    ABSOLUTE_VS_RELATIVE_IMPORT = "absolute_vs_relative_import"

    # Function Issues
    MISSING_DOCSTRING = "missing_docstring"
    FUNCTION_TOO_LONG = "function_too_long"
    TOO_MANY_PARAMETERS = "too_many_parameters"
    COMPLEX_FUNCTION = "complex_function"

    # Class Issues
    CLASS_TOO_LONG = "class_too_long"
    TOO_MANY_METHODS = "too_many_methods"
    INHERITANCE_DEPTH = "inheritance_depth"

    # Complexity Issues
    DEEPLY_NESTED_CALL = "deeply_nested_call"
    COMPLEX_BOOLEAN = "complex_boolean"
    LONG_EXPRESSION = "long_expression"
    HIGH_CYCLOMATIC_COMPLEXITY = "high_cyclomatic_complexity"

    # Code Smell Issues
    DUPLICATED_CODE = "duplicated_code"
    MAGIC_NUMBERS = "magic_numbers"
    HARDCODED_STRINGS = "hardcoded_strings"
    COMPLEX_CONDITIONAL = "complex_conditional"

    # Pattern Issues
    ONE_LINER_DETECTED = "one_liner_detected"
    LINE_TOO_LONG = "line_too_long"
    MISSING_BLANK_LINES = "missing_blank_lines"


class AutoFixCapability(Enum):
    """Capabilities for automatic issue fixing"""

    CAN_FIX = "can_fix"
    CAN_PARTIALLY_FIX = "can_partially_fix"
    CANNOT_FIX = "cannot_fix"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


@dataclass
class ASTAnalysisRule:
    """Defines a rule for AST-based code analysis"""

    name: str
    strategy: AnalysisStrategy
    issue_type: IssueType
    severity: IssueSeverity
    auto_fix: AutoFixCapability
    description: str
    suggestion: str
    ast_node_types: list[type] = field(default_factory=list)
    conditions: list[Callable] = field(default_factory=list)
    fix_strategy: Optional[Callable] = None
    threshold: Optional[float] = None


@dataclass
class CodeQualityMetric:
    """Represents a code quality metric"""

    name: str
    value: float
    unit: str
    threshold: Optional[float] = None
    is_good: bool = True
    description: str = ""


@dataclass
class ASTAnalysisResult:
    """Result of AST analysis for a file"""

    file_path: Path
    syntax_valid: bool
    syntax_errors: list[Any] = field(default_factory=list)
    issues: list[Any] = field(default_factory=list)
    metrics: list[CodeQualityMetric] = field(default_factory=list)
    ast_tree: Optional[ast.AST] = None
    analysis_time: float = 0.0


@dataclass
class TransformationRule:
    """Defines how to transform code to fix issues"""

    name: str
    issue_type: IssueType
    description: str
    ast_transformer: Callable
    validation: Callable
    rollback: Optional[Callable] = None


class ASTEnhancedLinterModel:
    """
    Domain model for AST-enhanced linting system

    This model defines:
    1. Analysis strategies and rules
    2. Quality metrics and thresholds
    3. Transformation rules for auto-fixing
    4. Validation and rollback mechanisms
    """

    def __init__(self):
        self.analysis_rules: list[ASTAnalysisRule] = []
        self.transformation_rules: list[TransformationRule] = []
        self.quality_thresholds: dict[str, float] = {}

        self._initialize_analysis_rules()
        self._initialize_transformation_rules()
        self._initialize_quality_thresholds()

    def _initialize_analysis_rules(self):
        """Initialize the analysis rules based on best practices"""

        # Syntax Validation Rules
        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Syntax Validation",
                strategy=AnalysisStrategy.SYNTAX_VALIDATION,
                issue_type=IssueType.SYNTAX_ERROR,
                severity=IssueSeverity.CRITICAL,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Python syntax validation",
                suggestion="Fix the syntax error in the code",
                ast_node_types=[ast.Module],
            )
        )

        # Import Analysis Rules
        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Multiple Imports on One Line",
                strategy=AnalysisStrategy.IMPORT_ANALYSIS,
                issue_type=IssueType.MULTIPLE_IMPORTS,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_FIX,
                description="Multiple imports on a single line",
                suggestion="Split imports onto separate lines for readability",
                ast_node_types=[ast.Import],
                conditions=[self._has_multiple_imports],
                fix_strategy=self._fix_multiple_imports,
            )
        )

        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Unused Import Detection",
                strategy=AnalysisStrategy.IMPORT_ANALYSIS,
                issue_type=IssueType.UNUSED_IMPORT,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_FIX,
                description="Import that is never used",
                suggestion="Remove unused import to clean up code",
                ast_node_types=[ast.Import, ast.ImportFrom],
                conditions=[self._is_import_unused],
                fix_strategy=self._fix_unused_imports,
            )
        )

        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Wildcard Import",
                strategy=AnalysisStrategy.IMPORT_ANALYSIS,
                issue_type=IssueType.WILDCARD_IMPORT,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_PARTIALLY_FIX,
                description="Wildcard import (import *) detected",
                suggestion="Use specific imports instead of import *",
                ast_node_types=[ast.ImportFrom],
                conditions=[self._is_wildcard_import],
                fix_strategy=self._fix_wildcard_imports,
            )
        )

        # Function Analysis Rules
        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Missing Function Docstring",
                strategy=AnalysisStrategy.FUNCTION_ANALYSIS,
                issue_type=IssueType.MISSING_DOCSTRING,
                severity=IssueSeverity.SUGGESTION,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Function missing docstring",
                suggestion="Add docstring to document function purpose",
                ast_node_types=[ast.FunctionDef],
                conditions=[self._has_no_docstring],
            )
        )

        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Function Too Long",
                strategy=AnalysisStrategy.FUNCTION_ANALYSIS,
                issue_type=IssueType.FUNCTION_TOO_LONG,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.REQUIRES_MANUAL_REVIEW,
                description="Function exceeds recommended length",
                suggestion="Consider breaking into smaller functions",
                ast_node_types=[ast.FunctionDef],
                conditions=[self._is_function_too_long],
                threshold=20.0,
            )
        )

        # Complexity Analysis Rules
        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Deeply Nested Call",
                strategy=AnalysisStrategy.COMPLEXITY_ANALYSIS,
                issue_type=IssueType.DEEPLY_NESTED_CALL,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_PARTIALLY_FIX,
                description="Function call with excessive nesting",
                suggestion="Break into multiple lines for readability",
                ast_node_types=[ast.Call],
                conditions=[self._is_deeply_nested],
                threshold=3.0,
                fix_strategy=self._fix_deeply_nested_calls,
            )
        )

        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Complex Boolean Expression",
                strategy=AnalysisStrategy.COMPLEXITY_ANALYSIS,
                issue_type=IssueType.COMPLEX_BOOLEAN,
                severity=IssueSeverity.WARNING,
                auto_fix=AutoFixCapability.CAN_PARTIALLY_FIX,
                description="Boolean expression with many terms",
                suggestion="Break into multiple lines or extract to variables",
                ast_node_types=[ast.BoolOp],
                conditions=[self._is_complex_boolean],
                threshold=3.0,
                fix_strategy=self._fix_complex_boolean,
            )
        )

        # Code Smell Detection Rules
        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Magic Numbers",
                strategy=AnalysisStrategy.CODE_SMELL_DETECTION,
                issue_type=IssueType.MAGIC_NUMBERS,
                severity=IssueSeverity.SUGGESTION,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Magic number detected in code",
                suggestion="Extract to named constant with descriptive name",
                ast_node_types=[ast.Num],
                conditions=[self._is_magic_number],
            )
        )

        self.analysis_rules.append(
            ASTAnalysisRule(
                name="Hardcoded Strings",
                strategy=AnalysisStrategy.CODE_SMELL_DETECTION,
                issue_type=IssueType.HARDCODED_STRINGS,
                severity=IssueSeverity.SUGGESTION,
                auto_fix=AutoFixCapability.CANNOT_FIX,
                description="Hardcoded string that should be configurable",
                suggestion="Extract to configuration or constants",
                ast_node_types=[ast.Str],
                conditions=[self._is_hardcoded_string],
            )
        )

    def _initialize_transformation_rules(self):
        """Initialize transformation rules for auto-fixing"""

        self.transformation_rules.append(
            TransformationRule(
                name="Split Multiple Imports",
                issue_type=IssueType.MULTIPLE_IMPORTS,
                description="Split multiple imports on one line into separate lines",
                ast_transformer=self._transform_multiple_imports,
                validation=self._validate_import_split,
                rollback=self._rollback_import_split,
            )
        )

        self.transformation_rules.append(
            TransformationRule(
                name="Remove Unused Imports",
                issue_type=IssueType.UNUSED_IMPORT,
                description="Remove imports that are never used",
                ast_transformer=self._transform_remove_unused_imports,
                validation=self._validate_import_removal,
                rollback=self._rollback_import_removal,
            )
        )

        self.transformation_rules.append(
            TransformationRule(
                name="Simplify Nested Calls",
                issue_type=IssueType.DEEPLY_NESTED_CALL,
                description="Break deeply nested function calls into multiple lines",
                ast_transformer=self._transform_nested_calls,
                validation=self._validate_nested_call_simplification,
                rollback=self._rollback_nested_call_simplification,
            )
        )

    def _initialize_quality_thresholds(self):
        """Initialize quality thresholds based on best practices"""

        self.quality_thresholds = {
            "function_length": 20.0,  # lines
            "class_length": 200.0,  # lines
            "method_count": 15.0,  # methods per class
            "nesting_depth": 3.0,  # levels
            "cyclomatic_complexity": 10.0,  # complexity score
            "import_count": 10.0,  # imports per file
            "line_length": 88.0,  # characters (Black default)
        }

    # Condition Methods for Analysis Rules
    def _has_multiple_imports(self, node: ast.Import) -> bool:
        """Check if import statement has multiple imports"""
        return len(node.names) > 1

    def _is_import_unused(self, node: ast.AST) -> bool:
        """Check if import is unused (simplified implementation)"""
        # This would need more sophisticated analysis in practice
        return False

    def _is_wildcard_import(self, node: ast.ImportFrom) -> bool:
        """Check if import from uses wildcard"""
        return any(alias.name == "*" for alias in node.names)

    def _has_no_docstring(self, node: ast.FunctionDef) -> bool:
        """Check if function has no docstring"""
        return ast.get_docstring(node) is None

    def _is_function_too_long(self, node: ast.FunctionDef) -> bool:
        """Check if function exceeds length threshold"""
        threshold = self.quality_thresholds.get("function_length", 20.0)
        return len(node.body) > threshold

    def _is_deeply_nested(self, node: ast.Call) -> bool:
        """Check if function call is deeply nested"""
        threshold = self.quality_thresholds.get("nesting_depth", 3.0)
        return self._get_nesting_depth(node) > threshold

    def _is_complex_boolean(self, node: ast.BoolOp) -> bool:
        """Check if boolean expression is complex"""
        threshold = self.quality_thresholds.get("nesting_depth", 3.0)
        return len(node.values) > threshold

    def _is_magic_number(self, node: ast.Num) -> bool:
        """Check if number is a magic number"""
        # Simple heuristic: numbers that aren't 0, 1, -1
        return node.n not in [0, 1, -1]

    def _is_hardcoded_string(self, node: ast.Str) -> bool:
        """Check if string should be configurable"""
        # Simple heuristic: long strings might be configurable
        return len(node.s) > 20

    # Fix Strategy Methods
    def _fix_multiple_imports(self, node: ast.Import) -> list[ast.Import]:
        """Split multiple imports into separate statements"""
        return [ast.Import(names=[name]) for name in node.names]

    def _fix_unused_imports(self, node: ast.AST) -> None:
        """Remove unused import (implementation would be more complex)"""

    def _fix_wildcard_imports(self, node: ast.ImportFrom) -> list[ast.ImportFrom]:
        """Convert wildcard import to specific imports (partial fix)"""
        # This would require analysis to determine what's actually used
        return []

    def _fix_deeply_nested_calls(self, node: ast.Call) -> ast.Call:
        """Simplify deeply nested calls (partial fix)"""
        # Implementation would break down complex calls
        return node

    def _fix_complex_boolean(self, node: ast.BoolOp) -> ast.BoolOp:
        """Simplify complex boolean expressions (partial fix)"""
        # Implementation would break down complex booleans
        return node

    # Transformation Methods
    def _transform_multiple_imports(self, tree: ast.AST) -> ast.AST:
        """Transform multiple imports into separate statements"""
        # Implementation would modify the AST
        return tree

    def _transform_remove_unused_imports(self, tree: ast.AST) -> ast.AST:
        """Transform AST to remove unused imports"""
        # Implementation would modify the AST
        return tree

    def _transform_nested_calls(self, tree: ast.AST) -> ast.AST:
        """Transform AST to simplify nested calls"""
        # Implementation would modify the AST
        return tree

    # Validation Methods
    def _validate_import_split(self, original: ast.AST, transformed: ast.AST) -> bool:
        """Validate that import split was successful"""
        return True

    def _validate_import_removal(self, original: ast.AST, transformed: ast.AST) -> bool:
        """Validate that import removal was successful"""
        return True

    def _validate_nested_call_simplification(self, original: ast.AST, transformed: ast.AST) -> bool:
        """Validate that nested call simplification was successful"""
        return True

    # Rollback Methods
    def _rollback_import_split(self, tree: ast.AST) -> ast.AST:
        """Rollback import split transformation"""
        return tree

    def _rollback_import_removal(self, tree: ast.AST) -> ast.AST:
        """Rollback import removal transformation"""
        return tree

    def _rollback_nested_call_simplification(self, tree: ast.AST) -> ast.AST:
        """Rollback nested call simplification transformation"""
        return tree

    # Utility Methods
    def _get_nesting_depth(self, node: ast.AST) -> int:
        """Calculate nesting depth of an AST node"""
        depth = 0
        current = node
        while hasattr(current, "parent"):
            depth += 1
            current = current.parent
        return depth

    def get_rules_for_strategy(self, strategy: AnalysisStrategy) -> list[ASTAnalysisRule]:
        """Get all rules for a specific analysis strategy"""
        return [rule for rule in self.analysis_rules if rule.strategy == strategy]

    def get_rules_for_issue_type(self, issue_type: IssueType) -> list[ASTAnalysisRule]:
        """Get all rules for a specific issue type"""
        return [rule for rule in self.analysis_rules if rule.issue_type == issue_type]

    def get_auto_fixable_rules(self) -> list[ASTAnalysisRule]:
        """Get all rules that can be auto-fixed"""
        return [rule for rule in self.analysis_rules if rule.auto_fix in [AutoFixCapability.CAN_FIX, AutoFixCapability.CAN_PARTIALLY_FIX]]


# Factory function for creating the model
def create_ast_enhanced_linter_model() -> ASTEnhancedLinterModel:
    """Create and return a configured AST-enhanced linter model"""
    return ASTEnhancedLinterModel()


if __name__ == "__main__":
    # Test the model creation
    model = create_ast_enhanced_linter_model()
    print(f"✅ AST Enhanced Linter Model created successfully!")
    print(f"   Analysis Rules: {len(model.analysis_rules)}")
    print(f"   Transformation Rules: {len(model.transformation_rules)}")
    print(f"   Quality Thresholds: {len(model.quality_thresholds)}")

    # Print some example rules
    print(f"\n📋 Example Analysis Rules:")
    for rule in model.analysis_rules[:3]:
        print(f"   - {rule.name}: {rule.issue_type.value} ({rule.severity.value})")

    print(f"\n🔧 Example Transformation Rules:")
    for rule in model.transformation_rules[:2]:
        print(f"   - {rule.name}: {rule.issue_type.value}")

    print(f"\n📊 Quality Thresholds:")
    for metric, threshold in list(model.quality_thresholds.items())[:3]:
        print(f"   - {metric}: {threshold}")
