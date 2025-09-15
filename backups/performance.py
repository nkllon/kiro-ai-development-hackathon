"""
Performance Expert Agent

Provides systematic analysis of performance bottlenecks,
optimization opportunities, and performance best practices.
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging

from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import (
    AnalysisResult,
    AnalysisContext,
    Finding,
    Recommendation,
    FindingType,
    Severity,
    CodeLocation,
)

logger = logging.getLogger(__name__)


class PerformanceExpert(GhostbustersExpertAgent):
    """
    Expert agent for performance analysis.

    Analyzes code for performance bottlenecks, inefficient algorithms,
    and optimization opportunities with systematic confidence scoring.
    """

    def __init__(self, name: str = "PerformanceExpert", version: str = "1.0.0"):
        super().__init__(name, version)
        self._capabilities = [
            "algorithm_analysis",
            "complexity_analysis",
            "memory_usage_analysis",
            "io_optimization_analysis",
            "database_query_analysis",
            "caching_analysis",
            "concurrency_analysis",
            "resource_leak_detection",
        ]

        # Performance anti-patterns and issues
        self._init_performance_patterns()

        logger.info(f"PerformanceExpert {version} initialized")

    def _init_performance_patterns(self):
        """Initialize performance patterns and anti-patterns"""

        # Inefficient patterns
        self.inefficient_patterns = {
            "nested_loops": [
                r"for\s+\w+\s+in.*:\s*\n.*for\s+\w+\s+in",
                r"while.*:\s*\n.*while",
            ],
            "string_concatenation": [
                r'\w+\s*\+=\s*["\'].*["\']',
                r'\w+\s*=\s*\w+\s*\+\s*["\']',
            ],
            "inefficient_search": [
                r"for\s+\w+\s+in\s+\w+:\s*\n.*if\s+\w+\s*==",
                r"\.index\s*\(",
                r"\.count\s*\(",
            ],
            "repeated_computation": [
                r"len\s*\(\s*\w+\s*\)\s*.*for",
                r"\.upper\s*\(\s*\)\s*.*for",
                r"\.lower\s*\(\s*\)\s*.*for",
            ],
        }

        # Database performance issues
        self.db_patterns = {
            "n_plus_one": [
                r"for\s+\w+\s+in.*:\s*\n.*\.get\s*\(",
                r"for\s+\w+\s+in.*:\s*\n.*\.filter\s*\(",
            ],
            "missing_indexes": [r"\.filter\s*\(\s*\w+\s*=", r"WHERE\s+\w+\s*="],
            "select_star": [r"SELECT\s+\*\s+FROM", r"\.all\s*\(\s*\)"],
        }

        # Memory issues
        self.memory_patterns = {
            "memory_leaks": [
                r"global\s+\w+\s*=\s*\[\]",
                r"class\s+\w+.*:\s*\n.*\w+\s*=\s*\[\]",
            ],
            "large_objects": [
                r"range\s*\(\s*\d{6,}",  # Large ranges
                r"\[\s*.*\s*for\s+.*\s+in\s+range\s*\(\s*\d{4,}",  # Large list comprehensions
            ],
        }

        # I/O performance issues
        self.io_patterns = {
            "synchronous_io": [
                r"open\s*\(.*\)\s*\.read\s*\(\s*\)",
                r"requests\.get\s*\(",
                r"urllib\.request",
            ],
            "unbuffered_io": [
                r"open\s*\([^)]*\)\s*\.readline\s*\(\s*\)",
                r"\.write\s*\(\s*.*\s*\)\s*\n.*\.write",
            ],
        }

        # Concurrency issues
        self.concurrency_patterns = {
            "blocking_operations": [
                r"time\.sleep\s*\(",
                r"input\s*\(",
                r"\.join\s*\(\s*\)",
            ],
            "race_conditions": [r"global\s+\w+", r"threading\.Thread.*target"],
        }

    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """
        Perform comprehensive performance analysis.

        Args:
            context: Analysis context with target path and configuration

        Returns:
            AnalysisResult with performance findings and recommendations
        """
        start_time = __import__("time").time()
        findings = []
        recommendations = []

        try:
            target_path = Path(context.target_path)

            if target_path.is_dir():
                # Analyze project performance
                findings.extend(await self._analyze_project_performance(target_path))
            elif target_path.is_file():
                # Analyze single file performance
                findings.extend(await self._analyze_file_performance(target_path))
            else:
                raise FileNotFoundError(f"Target not found: {target_path}")

            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(findings)

            # Calculate confidence
            confidence = self._calculate_performance_confidence(findings, target_path)

            analysis_duration = __import__("time").time() - start_time

            result = AnalysisResult(
                agent_name=self.name,
                confidence=confidence,
                findings=findings,
                recommendations=recommendations,
                analysis_duration=analysis_duration,
                context=context,
                metadata={
                    "performance_issues_detected": self._get_detected_issues(findings),
                    "complexity_analysis": self._get_complexity_analysis(findings),
                    "optimization_opportunities": self._get_optimization_opportunities(
                        findings
                    ),
                },
            )

            logger.info(
                f"Performance analysis completed for {target_path} with {len(findings)} findings"
            )
            return result

        except Exception as e:
            logger.error(
                f"Performance analysis failed for {context.target_path}: {str(e)}"
            )

            analysis_duration = __import__("time").time() - start_time
            return AnalysisResult(
                agent_name=self.name,
                confidence=0.0,
                findings=[
                    Finding(
                        type=FindingType.PERFORMANCE_ISSUE,
                        severity=Severity.CRITICAL,
                        description=f"Performance analysis failed: {str(e)}",
                        confidence=1.0,
                    )
                ],
                recommendations=[
                    Recommendation(
                        title="Fix Analysis Error",
                        description=f"Resolve performance analysis issue: {str(e)}",
                        priority=Severity.CRITICAL,
                    )
                ],
                analysis_duration=analysis_duration,
                context=context,
            )

    def get_capabilities(self) -> List[str]:
        """Return list of performance analysis capabilities"""
        return self._capabilities.copy()

    def validate_confidence(self, result: AnalysisResult) -> bool:
        """Validate confidence score accuracy"""
        if not 0.0 <= result.confidence <= 1.0:
            return False

        # High confidence should correlate with detected performance issues
        if result.confidence > 0.8:
            return "performance_issues_detected" in result.metadata

        return True

    async def _analyze_project_performance(self, directory: Path) -> List[Finding]:
        """Analyze project-level performance"""
        findings = []

        # Analyze all relevant files
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self._should_analyze_file(file_path):
                try:
                    findings.extend(await self._analyze_file_performance(file_path))
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {str(e)}")

        # Project-level performance analysis
        findings.extend(self._analyze_project_structure_performance(directory))

        return findings

    async def _analyze_file_performance(self, file_path: Path) -> List[Finding]:
        """Analyze single file performance"""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Language-specific analysis
            if file_path.suffix == ".py":
                findings.extend(
                    await self._analyze_python_performance(content, file_path)
                )
            elif file_path.suffix in [".js", ".ts"]:
                findings.extend(
                    await self._analyze_javascript_performance(content, file_path)
                )
            elif file_path.suffix == ".sql":
                findings.extend(await self._analyze_sql_performance(content, file_path))
            else:
                # Generic performance analysis
                findings.extend(
                    await self._analyze_generic_performance(content, file_path)
                )

        except Exception as e:
            findings.append(
                Finding(
                    type=FindingType.PERFORMANCE_ISSUE,
                    severity=Severity.LOW,
                    location=CodeLocation(str(file_path), 1),
                    description=f"Could not analyze file performance: {str(e)}",
                    confidence=0.6,
                )
            )

        return findings

    async def _analyze_python_performance(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Analyze Python code performance"""
        findings = []

        try:
            # Parse AST for detailed analysis
            tree = ast.parse(content)
            findings.extend(
                self._analyze_python_ast_performance(tree, content, file_path)
            )
        except SyntaxError:
            # Fall back to regex analysis
            pass

        # Pattern-based analysis
        findings.extend(self._check_performance_patterns(content, file_path))

        return findings

    def _analyze_python_ast_performance(
        self, tree: ast.AST, content: str, file_path: Path
    ) -> List[Finding]:
        """Analyze Python AST for performance issues"""
        findings = []

        class PerformanceVisitor(ast.NodeVisitor):
            def __init__(self, findings_list, file_path):
                self.findings = findings_list
                self.file_path = file_path
                self.loop_depth = 0
                self.in_loop = False

            def visit_For(self, node):
                self.loop_depth += 1
                old_in_loop = self.in_loop
                self.in_loop = True

                # Check for nested loops (O(n²) complexity)
                if self.loop_depth > 1:
                    self.findings.append(
                        Finding(
                            type=FindingType.PERFORMANCE_ISSUE,
                            severity=Severity.MEDIUM,
                            location=CodeLocation(str(self.file_path), node.lineno),
                            description=f"Nested loop detected (depth: {self.loop_depth}) - potential O(n²) complexity",
                            confidence=0.8,
                            evidence={
                                "issue": "nested_loops",
                                "depth": self.loop_depth,
                            },
                        )
                    )

                # Check for inefficient operations inside loops
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr in ["append", "extend"] and isinstance(
                                child.func.value, ast.Name
                            ):
                                # List operations in loop - potential performance issue
                                self.findings.append(
                                    Finding(
                                        type=FindingType.PERFORMANCE_ISSUE,
                                        severity=Severity.LOW,
                                        location=CodeLocation(
                                            str(self.file_path),
                                            getattr(child, "lineno", node.lineno),
                                        ),
                                        description=f"List.{child.func.attr}() in loop - consider list comprehension or pre-allocation",
                                        confidence=0.7,
                                        evidence={
                                            "issue": "list_operations_in_loop",
                                            "operation": child.func.attr,
                                        },
                                    )
                                )

                self.generic_visit(node)
                self.loop_depth -= 1
                self.in_loop = old_in_loop

            def visit_While(self, node):
                self.loop_depth += 1
                old_in_loop = self.in_loop
                self.in_loop = True

                if self.loop_depth > 1:
                    self.findings.append(
                        Finding(
                            type=FindingType.PERFORMANCE_ISSUE,
                            severity=Severity.MEDIUM,
                            location=CodeLocation(str(self.file_path), node.lineno),
                            description=f"Nested while loop detected (depth: {self.loop_depth})",
                            confidence=0.8,
                            evidence={
                                "issue": "nested_loops",
                                "depth": self.loop_depth,
                            },
                        )
                    )

                self.generic_visit(node)
                self.loop_depth -= 1
                self.in_loop = old_in_loop

            def visit_Call(self, node):
                # Check for inefficient function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id == "len" and self.in_loop:
                        self.findings.append(
                            Finding(
                                type=FindingType.PERFORMANCE_ISSUE,
                                severity=Severity.LOW,
                                location=CodeLocation(str(self.file_path), node.lineno),
                                description="len() called in loop - consider caching the result",
                                confidence=0.7,
                                evidence={"issue": "repeated_len_call"},
                            )
                        )

                elif isinstance(node.func, ast.Attribute):
                    # Check for string concatenation in loops
                    if node.func.attr in ["join"] and self.in_loop:
                        # This is actually good - joining in loop
                        pass
                    elif node.func.attr in ["upper", "lower", "strip"] and self.in_loop:
                        self.findings.append(
                            Finding(
                                type=FindingType.PERFORMANCE_ISSUE,
                                severity=Severity.LOW,
                                location=CodeLocation(str(self.file_path), node.lineno),
                                description=f"String.{node.func.attr}() in loop - consider caching if used repeatedly",
                                confidence=0.6,
                                evidence={
                                    "issue": "repeated_string_operation",
                                    "operation": node.func.attr,
                                },
                            )
                        )

                self.generic_visit(node)

            def visit_BinOp(self, node):
                # Check for string concatenation with +
                if isinstance(node.op, ast.Add) and self.in_loop:
                    # This could be string concatenation - check if operands are strings
                    self.findings.append(
                        Finding(
                            type=FindingType.PERFORMANCE_ISSUE,
                            severity=Severity.MEDIUM,
                            location=CodeLocation(str(self.file_path), node.lineno),
                            description="String concatenation with + in loop - consider using join() or f-strings",
                            confidence=0.6,
                            evidence={"issue": "string_concatenation_in_loop"},
                        )
                    )

                self.generic_visit(node)

        visitor = PerformanceVisitor(findings, file_path)
        visitor.visit(tree)

        return findings

    def _check_performance_patterns(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Check for performance anti-patterns using regex"""
        findings = []
        lines = content.splitlines()

        # Check all pattern categories
        all_patterns = {
            **self.inefficient_patterns,
            **self.db_patterns,
            **self.memory_patterns,
            **self.io_patterns,
            **self.concurrency_patterns,
        }

        for issue_type, patterns in all_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    severity = self._get_issue_severity(issue_type)
                    confidence = self._get_issue_confidence(issue_type)

                    findings.append(
                        Finding(
                            type=FindingType.PERFORMANCE_ISSUE,
                            severity=severity,
                            location=CodeLocation(str(file_path), line_num),
                            description=self._get_issue_description(issue_type),
                            confidence=confidence,
                            evidence={"issue": issue_type, "pattern": pattern},
                        )
                    )

        return findings

    async def _analyze_javascript_performance(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Analyze JavaScript performance"""
        findings = []
        lines = content.splitlines()

        js_patterns = {
            "dom_queries_in_loop": [r"for\s*\(.*\)\s*\{[^}]*document\.querySelector"],
            "inefficient_array_methods": [r"\.forEach\s*\([^)]*\.push"],
            "memory_leaks": [r"setInterval\s*\(", r"addEventListener\s*\("],
            "blocking_operations": [r"alert\s*\(", r"confirm\s*\(", r"prompt\s*\("],
        }

        for issue_type, patterns in js_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    findings.append(
                        Finding(
                            type=FindingType.PERFORMANCE_ISSUE,
                            severity=Severity.MEDIUM,
                            location=CodeLocation(str(file_path), line_num),
                            description=f"JavaScript performance issue: {issue_type.replace('_', ' ')}",
                            confidence=0.7,
                            evidence={"issue": issue_type, "language": "javascript"},
                        )
                    )

        return findings

    async def _analyze_sql_performance(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Analyze SQL performance"""
        findings = []

        sql_patterns = {
            "select_star": [
                r"SELECT\s+\*\s+FROM",
                "Avoid SELECT * - specify columns explicitly",
            ],
            "missing_where": [
                r"DELETE\s+FROM\s+\w+\s*;",
                "DELETE without WHERE clause",
            ],
            "cartesian_join": [r"FROM\s+\w+\s*,\s*\w+", "Potential cartesian join"],
            "function_in_where": [
                r"WHERE\s+\w+\s*\(\s*\w+\s*\)",
                "Function in WHERE clause prevents index usage",
            ],
        }

        for issue_type, (pattern, description) in sql_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1

                findings.append(
                    Finding(
                        type=FindingType.PERFORMANCE_ISSUE,
                        severity=Severity.MEDIUM,
                        location=CodeLocation(str(file_path), line_num),
                        description=f"SQL performance issue: {description}",
                        confidence=0.8,
                        evidence={"issue": issue_type, "language": "sql"},
                    )
                )

        return findings

    async def _analyze_generic_performance(
        self, content: str, file_path: Path
    ) -> List[Finding]:
        """Generic performance analysis"""
        findings = []

        # Check file size
        lines = content.splitlines()
        if len(lines) > 5000:
            findings.append(
                Finding(
                    type=FindingType.PERFORMANCE_ISSUE,
                    severity=Severity.LOW,
                    location=CodeLocation(str(file_path), 1),
                    description=f"Very large file ({len(lines)} lines) may impact performance",
                    confidence=0.6,
                    evidence={"issue": "large_file", "lines": len(lines)},
                )
            )

        return findings

    def _analyze_project_structure_performance(self, directory: Path) -> List[Finding]:
        """Analyze project structure for performance issues"""
        findings = []

        # Check for too many files in single directory
        python_files = list(directory.glob("*.py"))
        if len(python_files) > 50:
            findings.append(
                Finding(
                    type=FindingType.PERFORMANCE_ISSUE,
                    severity=Severity.LOW,
                    location=CodeLocation(str(directory), 1),
                    description=f"Too many files in single directory ({len(python_files)}) - may impact import performance",
                    confidence=0.6,
                    evidence={"issue": "too_many_files", "count": len(python_files)},
                )
            )

        return findings

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for performance"""
        # Analyze code files
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".sql",
            ".go",
            ".rs",
        }
        return file_path.suffix.lower() in code_extensions

    def _get_issue_severity(self, issue_type: str) -> Severity:
        """Get severity for issue type"""
        high_severity = {"nested_loops", "n_plus_one", "memory_leaks", "select_star"}
        medium_severity = {
            "string_concatenation",
            "inefficient_search",
            "synchronous_io",
        }

        if issue_type in high_severity:
            return Severity.HIGH
        elif issue_type in medium_severity:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def _get_issue_confidence(self, issue_type: str) -> float:
        """Get confidence for issue type"""
        high_confidence = {"nested_loops", "string_concatenation", "select_star"}
        medium_confidence = {"n_plus_one", "memory_leaks", "inefficient_search"}

        if issue_type in high_confidence:
            return 0.8
        elif issue_type in medium_confidence:
            return 0.7
        else:
            return 0.6

    def _get_issue_description(self, issue_type: str) -> str:
        """Get description for issue type"""
        descriptions = {
            "nested_loops": "Nested loops detected - potential O(n²) complexity",
            "string_concatenation": "Inefficient string concatenation - consider using join()",
            "inefficient_search": "Inefficient search pattern - consider using sets or dictionaries",
            "repeated_computation": "Repeated computation in loop - consider caching",
            "n_plus_one": "Potential N+1 query problem - consider using joins or prefetch",
            "missing_indexes": "Query may benefit from database index",
            "select_star": "SELECT * query - specify columns explicitly",
            "memory_leaks": "Potential memory leak - global or class-level mutable defaults",
            "large_objects": "Large object creation - consider generators or streaming",
            "synchronous_io": "Synchronous I/O operation - consider async alternatives",
            "unbuffered_io": "Unbuffered I/O operations - consider buffering",
            "blocking_operations": "Blocking operation detected - may impact responsiveness",
            "race_conditions": "Potential race condition in concurrent code",
        }

        return descriptions.get(
            issue_type, f"Performance issue: {issue_type.replace('_', ' ')}"
        )

    async def _generate_performance_recommendations(
        self, findings: List[Finding]
    ) -> List[Recommendation]:
        """Generate performance-specific recommendations"""
        recommendations = []

        # Group findings by issue type
        issue_types = {}
        for finding in findings:
            issue_type = finding.evidence.get("issue", "unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(finding)

        # Generate recommendations for each issue type
        for issue_type, issue_findings in issue_types.items():
            if issue_type == "nested_loops":
                recommendations.append(
                    Recommendation(
                        title="Optimize Nested Loops",
                        description=f"Refactor {len(issue_findings)} nested loop(s) to reduce complexity",
                        priority=Severity.HIGH,
                        effort_estimate="1-2 hours per loop",
                        automated_fix_available=False,
                    )
                )

            elif issue_type == "string_concatenation":
                recommendations.append(
                    Recommendation(
                        title="Optimize String Operations",
                        description=f"Replace {len(issue_findings)} string concatenation(s) with join() or f-strings",
                        priority=Severity.MEDIUM,
                        effort_estimate="15-30 minutes",
                        automated_fix_available=True,
                        fix_command="optimize_string_concat",
                    )
                )

            elif issue_type == "n_plus_one":
                recommendations.append(
                    Recommendation(
                        title="Fix N+1 Query Problems",
                        description=f"Optimize {len(issue_findings)} database query pattern(s)",
                        priority=Severity.HIGH,
                        effort_estimate="30-60 minutes per query",
                        automated_fix_available=False,
                    )
                )

        return recommendations

    def _calculate_performance_confidence(
        self, findings: List[Finding], target_path: Path
    ) -> float:
        """Calculate confidence score for performance analysis"""
        base_confidence = 0.7

        # Adjust based on file type
        if target_path.is_dir():
            code_files = [
                f
                for f in target_path.rglob("*")
                if f.suffix in {".py", ".js", ".ts", ".sql"}
            ]
            if code_files:
                base_confidence = 0.8
        elif target_path.suffix in {".py", ".js", ".ts", ".sql"}:
            base_confidence = 0.8

        # Adjust based on findings
        if findings:
            avg_confidence = sum(f.confidence for f in findings) / len(findings)
            base_confidence = (base_confidence + avg_confidence) / 2

        return min(1.0, max(0.0, base_confidence))

    def _get_detected_issues(self, findings: List[Finding]) -> List[str]:
        """Get list of detected performance issues"""
        issues = []
        for finding in findings:
            issue_type = finding.evidence.get("issue", "unknown")
            if issue_type not in issues:
                issues.append(issue_type)
        return issues

    def _get_complexity_analysis(self, findings: List[Finding]) -> Dict[str, int]:
        """Get complexity analysis from findings"""
        complexity = {
            "nested_loops": 0,
            "high_complexity": 0,
            "inefficient_algorithms": 0,
        }

        for finding in findings:
            issue_type = finding.evidence.get("issue", "")
            if "nested" in issue_type:
                complexity["nested_loops"] += 1
            if finding.severity == Severity.HIGH:
                complexity["high_complexity"] += 1
            if "inefficient" in issue_type:
                complexity["inefficient_algorithms"] += 1

        return complexity

    def _get_optimization_opportunities(self, findings: List[Finding]) -> List[str]:
        """Get optimization opportunities from findings"""
        opportunities = []

        for finding in findings:
            issue_type = finding.evidence.get("issue", "")
            if issue_type == "string_concatenation":
                opportunities.append("Use join() or f-strings for string operations")
            elif issue_type == "nested_loops":
                opportunities.append(
                    "Consider algorithmic improvements or data structure changes"
                )
            elif issue_type == "n_plus_one":
                opportunities.append(
                    "Implement query optimization with joins or prefetch"
                )
            elif issue_type == "synchronous_io":
                opportunities.append("Consider async/await for I/O operations")

        return list(set(opportunities))
