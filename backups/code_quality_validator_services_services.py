"""
Code Quality Validator Services Services

This module was extracted from code_quality_validator_services.py
as part of RM-DDD compliance refactoring.
"""

import logging
import ast
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from ..models import ValidationResult, TechnicalAssessment


class CodeQualityAssessmentEngine:
    """
    Comprehensive code quality assessment engine.

    Analyzes Python code for complexity, maintainability, documentation,
    style, security, and performance issues to ensure hackathon submissions
    meet professional development standards.
    """

    def __init__(self, project_path: Path):
        """
        Initialize the code quality assessment engine.

        Args:
            project_path: Path to the project being analyzed
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.thresholds = {
            "complexity_max": 10,
            "function_length_max": 50,
            "class_length_max": 200,
            "documentation_min": 80,
            "maintainability_min": 7.0,
        }
        self.source_patterns = ["src/**/*.py", "*.py", "lib/**/*.py"]
        self.exclude_patterns = [
            "test_*.py",
            "*_test.py",
            "tests/**/*.py",
            "__pycache__/**",
            ".git/**",
            "venv/**",
            "env/**",
        ]
        self.logger.info(f"Code quality engine initialized for {self.project_path}")

    def assess_code_quality(self) -> CodeQualityReport:
        """
        Perform comprehensive code quality assessment.

        Returns:
            Detailed code quality report with scores and recommendations
        """
        self.logger.info("Starting comprehensive code quality assessment")
        try:
            source_files = self._discover_source_files()
            if not source_files:
                return self._create_empty_report("No Python source files found")
            self.logger.info(f"Analyzing {len(source_files)} source files")
            all_issues = []
            total_lines = 0
            complexity_scores = []
            maintainability_scores = []
            documentation_scores = []
            style_scores = []
            security_scores = []
            performance_scores = []
            for source_file in source_files:
                try:
                    file_analysis = self._analyze_file(source_file)
                    all_issues.extend(file_analysis["issues"])
                    total_lines += file_analysis["lines_of_code"]
                    complexity_scores.append(file_analysis["complexity_score"])
                    maintainability_scores.append(
                        file_analysis["maintainability_score"]
                    )
                    documentation_scores.append(file_analysis["documentation_score"])
                    style_scores.append(file_analysis["style_score"])
                    security_scores.append(file_analysis["security_score"])
                    performance_scores.append(file_analysis["performance_score"])
                except Exception as e:
                    self.logger.warning(f"Failed to analyze {source_file}: {e}")
                    all_issues.append(
                        CodeQualityIssue(
                            file_path=str(source_file),
                            line_number=1,
                            issue_type=CodeQualityMetric.MAINTAINABILITY,
                            severity="major",
                            message=f"Analysis failed: {e}",
                            suggestion="Fix syntax errors or file encoding issues",
                        )
                    )
            complexity_score = self._calculate_average_score(complexity_scores)
            maintainability_score = self._calculate_average_score(
                maintainability_scores
            )
            documentation_score = self._calculate_average_score(documentation_scores)
            style_score = self._calculate_average_score(style_scores)
            security_score = self._calculate_average_score(security_scores)
            performance_score = self._calculate_average_score(performance_scores)
            overall_score = (
                complexity_score * 0.25
                + maintainability_score * 0.2
                + documentation_score * 0.2
                + style_score * 0.15
                + security_score * 0.1
                + performance_score * 0.1
            )
            critical_issues = [i for i in all_issues if i.severity == "critical"]
            major_issues = [i for i in all_issues if i.severity == "major"]
            minor_issues = [i for i in all_issues if i.severity == "minor"]
            recommendations = self._generate_recommendations(
                all_issues,
                {
                    "complexity": complexity_score,
                    "maintainability": maintainability_score,
                    "documentation": documentation_score,
                    "style": style_score,
                    "security": security_score,
                    "performance": performance_score,
                },
            )
            report = CodeQualityReport(
                overall_score=overall_score,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score,
                documentation_score=documentation_score,
                style_score=style_score,
                security_score=security_score,
                performance_score=performance_score,
                total_issues=len(all_issues),
                critical_issues=len(critical_issues),
                major_issues=len(major_issues),
                minor_issues=len(minor_issues),
                issues=all_issues,
                recommendations=recommendations,
                files_analyzed=len(source_files),
                lines_of_code=total_lines,
            )
            self.logger.info(
                f"Code quality assessment complete. Overall score: {overall_score:.1f}"
            )
            return report
        except Exception as e:
            self.logger.error(f"Code quality assessment failed: {e}")
            return self._create_empty_report(f"Assessment failed: {e}")

    def validate_code_quality(self, min_score: float = 80.0) -> ValidationResult:
        """
        Validate code quality against minimum standards.

        Args:
            min_score: Minimum acceptable quality score

        Returns:
            Validation result with quality assessment
        """
        report = self.assess_code_quality()
        issues = []
        recommendations = []
        if report.overall_score < min_score:
            issues.append(
                f"Code quality score too low: {report.overall_score:.1f} < {min_score}"
            )
        if report.critical_issues > 0:
            issues.append(
                f"Critical code quality issues found: {report.critical_issues}"
            )
            recommendations.append("Fix all critical code quality issues immediately")
        if report.major_issues > 5:
            issues.append(f"Too many major code quality issues: {report.major_issues}")
            recommendations.append(
                "Reduce major code quality issues to improve maintainability"
            )
        recommendations.extend(report.recommendations[:3])
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=report.overall_score,
            issues=issues,
            recommendations=recommendations,
        )

    def generate_quality_improvement_plan(self, report: CodeQualityReport) -> List[str]:
        """
        Generate systematic improvement plan based on quality assessment.

        Args:
            report: Code quality assessment report

        Returns:
            Prioritized list of improvement actions
        """
        improvement_plan = []
        if report.critical_issues > 0:
            improvement_plan.append("CRITICAL: Fix all critical code quality issues")
            critical_files = set(
                (
                    issue.file_path
                    for issue in report.issues
                    if issue.severity == "critical"
                )
            )
            for file_path in critical_files:
                improvement_plan.append(
                    f"  - Review and fix critical issues in {file_path}"
                )
        if report.complexity_score < 70:
            improvement_plan.append("HIGH: Reduce code complexity")
            improvement_plan.append(
                "  - Break down complex functions into smaller units"
            )
            improvement_plan.append(
                "  - Simplify conditional logic and nested structures"
            )
            improvement_plan.append(
                "  - Extract common functionality into helper functions"
            )
        if report.documentation_score < 80:
            improvement_plan.append("HIGH: Improve documentation coverage")
            improvement_plan.append(
                "  - Add docstrings to all public functions and classes"
            )
            improvement_plan.append(
                "  - Document complex algorithms and business logic"
            )
            improvement_plan.append("  - Add type hints for better code clarity")
        if report.maintainability_score < 70:
            improvement_plan.append("MEDIUM: Improve code maintainability")
            improvement_plan.append(
                "  - Refactor duplicate code into reusable functions"
            )
            improvement_plan.append("  - Improve variable and function naming")
            improvement_plan.append("  - Reduce coupling between modules")
        if report.style_score < 80:
            improvement_plan.append("MEDIUM: Improve code style consistency")
            improvement_plan.append(
                "  - Run automated code formatter (black, autopep8)"
            )
            improvement_plan.append("  - Fix linting issues (flake8, pylint)")
            improvement_plan.append("  - Ensure consistent naming conventions")
        if report.security_score < 90:
            improvement_plan.append("MEDIUM: Address security concerns")
            improvement_plan.append(
                "  - Review and fix potential security vulnerabilities"
            )
            improvement_plan.append("  - Validate all user inputs and external data")
            improvement_plan.append("  - Use secure coding practices")
        if report.performance_score < 80:
            improvement_plan.append("LOW: Optimize performance")
            improvement_plan.append("  - Profile and optimize slow code paths")
            improvement_plan.append(
                "  - Reduce unnecessary computations and memory usage"
            )
            improvement_plan.append("  - Consider algorithmic improvements")
        return improvement_plan

    def _discover_source_files(self) -> List[Path]:
        """Discover Python source files to analyze."""
        source_files = []
        for pattern in self.source_patterns:
            files = list(self.project_path.rglob(pattern))
            source_files.extend(files)
        filtered_files = []
        for file_path in source_files:
            should_exclude = False
            for exclude_pattern in self.exclude_patterns:
                if file_path.match(exclude_pattern):
                    should_exclude = True
                    break
            if not should_exclude and file_path.is_file():
                filtered_files.append(file_path)
        return filtered_files

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file for quality metrics."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            lines_of_code = len(
                [
                    line
                    for line in content.split("\n")
                    if line.strip() and (not line.strip().startswith("#"))
                ]
            )
            complexity_analysis = self._analyze_complexity(tree, file_path)
            maintainability_analysis = self._analyze_maintainability(
                tree, content, file_path
            )
            documentation_analysis = self._analyze_documentation(tree, file_path)
            style_analysis = self._analyze_style(content, file_path)
            security_analysis = self._analyze_security(tree, content, file_path)
            performance_analysis = self._analyze_performance(tree, content, file_path)
            all_issues = []
            all_issues.extend(complexity_analysis["issues"])
            all_issues.extend(maintainability_analysis["issues"])
            all_issues.extend(documentation_analysis["issues"])
            all_issues.extend(style_analysis["issues"])
            all_issues.extend(security_analysis["issues"])
            all_issues.extend(performance_analysis["issues"])
            return {
                "lines_of_code": lines_of_code,
                "complexity_score": complexity_analysis["score"],
                "maintainability_score": maintainability_analysis["score"],
                "documentation_score": documentation_analysis["score"],
                "style_score": style_analysis["score"],
                "security_score": security_analysis["score"],
                "performance_score": performance_analysis["score"],
                "issues": all_issues,
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")
            return {
                "lines_of_code": 0,
                "complexity_score": 0,
                "maintainability_score": 0,
                "documentation_score": 0,
                "style_score": 0,
                "security_score": 0,
                "performance_score": 0,
                "issues": [
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=1,
                        issue_type=CodeQualityMetric.MAINTAINABILITY,
                        severity="critical",
                        message=f"File analysis failed: {e}",
                        suggestion="Fix syntax errors or encoding issues",
                    )
                ],
            }

    def _analyze_complexity(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        issues = []
        complexity_scores = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                complexity_scores.append(min(100, max(0, 100 - (complexity - 1) * 10)))
                if complexity > self.thresholds["complexity_max"]:
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type=CodeQualityMetric.COMPLEXITY,
                            severity="major" if complexity > 15 else "minor",
                            message=f"Function '{node.name}' has high complexity: {complexity}",
                            suggestion="Break down into smaller functions or simplify logic",
                        )
                    )
                function_length = self._get_node_length(node)
                if function_length > self.thresholds["function_length_max"]:
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type=CodeQualityMetric.COMPLEXITY,
                            severity="minor",
                            message=f"Function '{node.name}' is too long: {function_length} lines",
                            suggestion="Break down into smaller, more focused functions",
                        )
                    )
            elif isinstance(node, ast.ClassDef):
                class_length = self._get_node_length(node)
                if class_length > self.thresholds["class_length_max"]:
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type=CodeQualityMetric.COMPLEXITY,
                            severity="minor",
                            message=f"Class '{node.name}' is too long: {class_length} lines",
                            suggestion="Consider breaking into smaller, more focused classes",
                        )
                    )
        avg_score = (
            sum(complexity_scores) / len(complexity_scores)
            if complexity_scores
            else 100
        )
        return {"score": avg_score, "issues": issues}

    def _analyze_maintainability(
        self, tree: ast.AST, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Analyze code maintainability metrics."""
        issues = []
        maintainability_score = 100
        lines = content.split("\n")
        line_counts = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 10 and (not stripped.startswith("#")):
                if stripped in line_counts:
                    line_counts[stripped].append(i + 1)
                else:
                    line_counts[stripped] = [i + 1]
        for line_content, line_numbers in line_counts.items():
            if len(line_numbers) > 2:
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_numbers[0],
                        issue_type=CodeQualityMetric.MAINTAINABILITY,
                        severity="minor",
                        message=f"Duplicated code found ({len(line_numbers)} occurrences)",
                        suggestion="Extract common code into reusable functions",
                    )
                )
                maintainability_score -= 5
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type=CodeQualityMetric.MAINTAINABILITY,
                            severity="minor",
                            message=f"Function '{node.name}' has too many parameters: {param_count}",
                            suggestion="Consider using a configuration object or breaking down the function",
                        )
                    )
                    maintainability_score -= 3
        return {"score": max(0, maintainability_score), "issues": issues}

    def _analyze_documentation(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """Analyze documentation coverage and quality."""
        issues = []
        total_items = 0
        documented_items = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                total_items += 1
                has_docstring = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )
                if has_docstring:
                    documented_items += 1
                    docstring = node.body[0].value.value
                    if len(docstring.strip()) < 10:
                        issues.append(
                            CodeQualityIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type=CodeQualityMetric.DOCUMENTATION,
                                severity="minor",
                                message=f"{type(node).__name__} '{node.name}' has minimal docstring",
                                suggestion="Provide more detailed documentation",
                            )
                        )
                else:
                    severity = "major" if isinstance(node, ast.ClassDef) else "minor"
                    issues.append(
                        CodeQualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type=CodeQualityMetric.DOCUMENTATION,
                            severity=severity,
                            message=f"{type(node).__name__} '{node.name}' missing docstring",
                            suggestion="Add comprehensive docstring with description and parameters",
                        )
                    )
        documentation_score = (
            documented_items / total_items * 100 if total_items > 0 else 100
        )
        return {"score": documentation_score, "issues": issues}

    def _analyze_style(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze code style and formatting."""
        issues = []
        style_score = 100
        lines = content.split("\n")
        for i, line in enumerate(lines):
            line_num = i + 1
            if len(line) > 120:
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=CodeQualityMetric.STYLE,
                        severity="minor",
                        message=f"Line too long: {len(line)} characters",
                        suggestion="Break long lines for better readability",
                    )
                )
                style_score -= 1
            if line.endswith(" ") or line.endswith("\t"):
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=CodeQualityMetric.STYLE,
                        severity="minor",
                        message="Trailing whitespace found",
                        suggestion="Remove trailing whitespace",
                    )
                )
                style_score -= 0.5
            if "\t" in line and "    " in line:
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=CodeQualityMetric.STYLE,
                        severity="major",
                        message="Mixed tabs and spaces for indentation",
                        suggestion="Use consistent indentation (prefer spaces)",
                    )
                )
                style_score -= 5
        return {"score": max(0, style_score), "issues": issues}

    def _analyze_security(
        self, tree: ast.AST, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Analyze potential security issues."""
        issues = []
        security_score = 100
        security_patterns = [
            ("eval\\s*\\(", "Use of eval() can be dangerous"),
            ("exec\\s*\\(", "Use of exec() can be dangerous"),
            ("subprocess\\.call\\s*\\(.*shell\\s*=\\s*True", "Shell injection risk"),
            ("os\\.system\\s*\\(", "Command injection risk"),
            ("pickle\\.loads?\\s*\\(", "Pickle deserialization can be unsafe"),
        ]
        for pattern, message in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=CodeQualityMetric.SECURITY,
                        severity="major",
                        message=message,
                        suggestion="Review for security implications and use safer alternatives",
                    )
                )
                security_score -= 10
        secret_patterns = [
            "password\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "api_key\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
            "secret\\s*=\\s*[\"\\'][^\"\\']+[\"\\']",
        ]
        for pattern in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    CodeQualityIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type=CodeQualityMetric.SECURITY,
                        severity="critical",
                        message="Potential hardcoded secret found",
                        suggestion="Use environment variables or secure configuration",
                    )
                )
                security_score -= 20
        return {"score": max(0, security_score), "issues": issues}

    def _analyze_performance(
        self, tree: ast.AST, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """Analyze potential performance issues."""
        issues = []
        performance_score = 100
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(
                        child.op, ast.Add
                    ):
                        if isinstance(child.target, ast.Name):
                            issues.append(
                                CodeQualityIssue(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    issue_type=CodeQualityMetric.PERFORMANCE,
                                    severity="minor",
                                    message="Potential inefficient list concatenation in loop",
                                    suggestion="Consider using list comprehension or join()",
                                )
                            )
                            performance_score -= 5
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "re"
                        and (node.func.attr in ["search", "match", "findall"])
                    ):
                        issues.append(
                            CodeQualityIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type=CodeQualityMetric.PERFORMANCE,
                                severity="minor",
                                message="Consider compiling regex patterns for repeated use",
                                suggestion="Use re.compile() for patterns used multiple times",
                            )
                        )
                        performance_score -= 2
        return {"score": max(0, performance_score), "issues": issues}

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function (simplified)."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _get_node_length(self, node: ast.AST) -> int:
        """Get the length of an AST node in lines."""
        if hasattr(node, "end_lineno") and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        else:
            return len(list(ast.walk(node)))

    def _calculate_average_score(self, scores: List[float]) -> float:
        """Calculate average score from a list of scores."""
        return sum(scores) / len(scores) if scores else 100.0

    def _generate_recommendations(
        self, issues: List[CodeQualityIssue], scores: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations based on issues and scores."""
        recommendations = []
        if scores["complexity"] < 70:
            recommendations.append(
                "Reduce code complexity by breaking down complex functions"
            )
        if scores["documentation"] < 80:
            recommendations.append(
                "Improve documentation coverage with comprehensive docstrings"
            )
        if scores["maintainability"] < 70:
            recommendations.append(
                "Improve maintainability by reducing code duplication"
            )
        if scores["style"] < 80:
            recommendations.append(
                "Improve code style consistency with automated formatting"
            )
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            recommendations.insert(
                0,
                f"Fix {len(critical_issues)} critical security/quality issues immediately",
            )
        security_issues = [
            i for i in issues if i.issue_type == CodeQualityMetric.SECURITY
        ]
        if security_issues:
            recommendations.append("Review and address security vulnerabilities")
        return recommendations[:5]

    def _create_empty_report(self, reason: str) -> CodeQualityReport:
        """Create an empty report with error information."""
        return CodeQualityReport(
            overall_score=0.0,
            complexity_score=0.0,
            maintainability_score=0.0,
            documentation_score=0.0,
            style_score=0.0,
            security_score=0.0,
            performance_score=0.0,
            total_issues=1,
            critical_issues=1,
            major_issues=0,
            minor_issues=0,
            issues=[
                CodeQualityIssue(
                    file_path="",
                    line_number=1,
                    issue_type=CodeQualityMetric.MAINTAINABILITY,
                    severity="critical",
                    message=reason,
                    suggestion="Ensure project has analyzable Python source files",
                )
            ],
            recommendations=[reason],
            files_analyzed=0,
            lines_of_code=0,
        )
