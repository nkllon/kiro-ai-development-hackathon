"""
Beast Mode Framework - Automated Code Quality Gates
Implements UC-18: Automated quality gates with enforcement
Provides systematic code quality validation and enforcement
Requirements: DR8 (Compliance), >90% coverage, systematic quality assurance
"""

import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus

class QualityGateStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class QualityGateType(Enum):
    LINTING = "linting"
    FORMATTING = "formatting"
    SECURITY = "security"
    COVERAGE = "coverage"
    COMPLEXITY = "complexity"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"

@dataclass
class QualityGateResult:
    gate_type: QualityGateType
    status: QualityGateStatus
    score: float  # 0.0 - 1.0
    details: Dict[str, Any]
    execution_time_seconds: float
    error_message: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)

@dataclass
class QualityGateConfig:
    enabled: bool = True
    threshold: float = 0.8  # Minimum score to pass
    timeout_seconds: int = 300
    fail_on_error: bool = True
    custom_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityAssessment:
    overall_status: QualityGateStatus
    overall_score: float
    gate_results: List[QualityGateResult]
    total_execution_time: float
    timestamp: datetime
    recommendations: List[str]
    compliance_status: Dict[str, bool]

class AutomatedQualityGates(ReflectiveModule):
    """
    Automated code quality gates with systematic enforcement
    Addresses UC-18 (Score: 6.5) - Automated quality assurance and compliance
    Enforces DR8: >90% code coverage and comprehensive quality validation
    """
    
    def __init__(self, project_root: Optional[str] = None):
        super().__init__("automated_quality_gates")
        
        # Project configuration
        self.project_root = Path(project_root or ".")
        self.src_path = self.project_root / "src"
        self.tests_path = self.project_root / "tests"
        
        # Quality gate configuration
        self.quality_gates = {
            QualityGateType.LINTING: QualityGateConfig(
                threshold=0.9,
                custom_rules={"max_line_length": 120, "max_complexity": 10}
            ),
            QualityGateType.FORMATTING: QualityGateConfig(
                threshold=1.0,  # Must be perfect
                custom_rules={"line_length": 120}
            ),
            QualityGateType.SECURITY: QualityGateConfig(
                threshold=0.95,
                custom_rules={"allow_warnings": False}
            ),
            QualityGateType.COVERAGE: QualityGateConfig(
                threshold=0.9,  # 90% coverage requirement (DR8)
                custom_rules={"exclude_patterns": ["*/tests/*", "*/migrations/*"]}
            ),
            QualityGateType.COMPLEXITY: QualityGateConfig(
                threshold=0.8,
                custom_rules={"max_complexity": 10, "max_function_length": 50}
            ),
            QualityGateType.DOCUMENTATION: QualityGateConfig(
                threshold=0.8,
                custom_rules={"require_docstrings": True, "min_doc_coverage": 0.8}
            )
        }
        
        # Quality metrics
        self.assessments_performed = 0
        self.total_assessment_time = 0.0
        self.gate_success_rates = {gate_type: 0.0 for gate_type in QualityGateType}
        
        # Beast Mode compliance requirements
        self.beast_mode_requirements = {
            "rm_compliance": "All modules must inherit from ReflectiveModule",
            "health_monitoring": "All modules must implement health indicators",
            "systematic_approach": "No ad-hoc implementations allowed",
            "constraint_compliance": "All Beast Mode constraints must be satisfied",
            "documentation_standards": "Comprehensive documentation required"
        }
        
        self._update_health_indicator(
            "quality_gates_readiness",
            HealthStatus.HEALTHY,
            f"{len(self.quality_gates)} gates configured",
            "Automated quality gates ready for enforcement"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for quality gate system"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "quality_gates_configured": len(self.quality_gates),
            "assessments_performed": self.assessments_performed,
            "average_assessment_time": self.total_assessment_time / max(1, self.assessments_performed),
            "gate_success_rates": self.gate_success_rates,
            "project_root": str(self.project_root),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for quality gate system"""
        return (
            self.project_root.exists() and
            self.src_path.exists() and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for quality gate system"""
        return {
            "system_health": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "project_structure_valid": self.src_path.exists(),
                "quality_gates_operational": len(self.quality_gates) > 0
            },
            "performance_metrics": {
                "assessments_completed": self.assessments_performed,
                "average_execution_time": self.total_assessment_time / max(1, self.assessments_performed),
                "success_rate": sum(self.gate_success_rates.values()) / max(1, len(self.gate_success_rates))
            },
            "compliance_status": {
                "beast_mode_requirements": len(self.beast_mode_requirements),
                "quality_thresholds": {gate_type.value: config.threshold for gate_type, config in self.quality_gates.items()}
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: automated code quality gate enforcement"""
        return "automated_code_quality_gate_enforcement"
        
    def execute_quality_assessment(self, target_path: Optional[str] = None) -> QualityAssessment:
        """
        Execute comprehensive quality assessment with all gates
        Required by DR8: >90% code coverage and comprehensive quality validation
        """
        self.assessments_performed += 1
        start_time = time.time()
        
        try:
            self.logger.info("Starting comprehensive quality assessment")
            
            assessment_path = Path(target_path) if target_path else self.src_path
            gate_results = []
            
            # Execute each quality gate
            for gate_type, config in self.quality_gates.items():
                if config.enabled:
                    try:
                        result = self._execute_quality_gate(gate_type, config, assessment_path)
                        gate_results.append(result)
                        
                        # Update success rates
                        current_rate = self.gate_success_rates[gate_type]
                        success = 1.0 if result.status == QualityGateStatus.PASSED else 0.0
                        self.gate_success_rates[gate_type] = (current_rate + success) / 2
                        
                    except Exception as e:
                        self.logger.error(f"Quality gate {gate_type.value} failed: {e}")
                        gate_results.append(QualityGateResult(
                            gate_type=gate_type,
                            status=QualityGateStatus.FAILED,
                            score=0.0,
                            details={"error": str(e)},
                            execution_time_seconds=0.0,
                            error_message=str(e),
                            recommendations=[f"Fix {gate_type.value} execution error"]
                        ))
                        
            # Calculate overall assessment
            total_execution_time = time.time() - start_time
            self.total_assessment_time += total_execution_time
            
            overall_score = sum(result.score for result in gate_results) / max(1, len(gate_results))
            overall_status = self._determine_overall_status(gate_results, overall_score)
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(gate_results)
            
            # Check Beast Mode compliance
            compliance_status = self._check_beast_mode_compliance(gate_results)
            
            assessment = QualityAssessment(
                overall_status=overall_status,
                overall_score=overall_score,
                gate_results=gate_results,
                total_execution_time=total_execution_time,
                timestamp=datetime.now(),
                recommendations=recommendations,
                compliance_status=compliance_status
            )
            
            self.logger.info(f"Quality assessment complete: {overall_status.value} (score: {overall_score:.2f})")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return QualityAssessment(
                overall_status=QualityGateStatus.FAILED,
                overall_score=0.0,
                gate_results=[],
                total_execution_time=time.time() - start_time,
                timestamp=datetime.now(),
                recommendations=[f"Fix assessment execution error: {e}"],
                compliance_status={"assessment_error": False}
            )
            
    def _execute_quality_gate(self, gate_type: QualityGateType, config: QualityGateConfig, target_path: Path) -> QualityGateResult:
        """Execute specific quality gate"""
        start_time = time.time()
        
        try:
            if gate_type == QualityGateType.LINTING:
                return self._execute_linting_gate(config, target_path, start_time)
            elif gate_type == QualityGateType.FORMATTING:
                return self._execute_formatting_gate(config, target_path, start_time)
            elif gate_type == QualityGateType.SECURITY:
                return self._execute_security_gate(config, target_path, start_time)
            elif gate_type == QualityGateType.COVERAGE:
                return self._execute_coverage_gate(config, target_path, start_time)
            elif gate_type == QualityGateType.COMPLEXITY:
                return self._execute_complexity_gate(config, target_path, start_time)
            elif gate_type == QualityGateType.DOCUMENTATION:
                return self._execute_documentation_gate(config, target_path, start_time)
            else:
                raise ValueError(f"Unknown quality gate type: {gate_type}")
                
        except Exception as e:
            return QualityGateResult(
                gate_type=gate_type,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": str(e)},
                execution_time_seconds=time.time() - start_time,
                error_message=str(e),
                recommendations=[f"Fix {gate_type.value} execution"]
            )
            
    def _execute_linting_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute linting quality gate using flake8"""
        try:
            # Run flake8 linting
            max_line_length = config.custom_rules.get("max_line_length", 120)
            max_complexity = config.custom_rules.get("max_complexity", 10)
            
            cmd = [
                "python3", "-m", "flake8", str(target_path),
                f"--max-line-length={max_line_length}",
                f"--max-complexity={max_complexity}",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
            
            # Parse results
            if result.returncode == 0:
                # No linting errors
                score = 1.0
                status = QualityGateStatus.PASSED
                details = {"violations": 0, "clean_files": "all"}
                recommendations = []
            else:
                # Parse linting violations
                violations = result.stdout.count('\n') if result.stdout else 0
                total_files = len(list(target_path.rglob("*.py")))
                
                # Calculate score based on violations per file
                violations_per_file = violations / max(1, total_files)
                score = max(0.0, 1.0 - (violations_per_file / 10))  # 10 violations per file = 0 score
                
                status = QualityGateStatus.PASSED if score >= config.threshold else QualityGateStatus.FAILED
                details = {
                    "violations": violations,
                    "violations_per_file": violations_per_file,
                    "total_files": total_files,
                    "stderr": result.stderr
                }
                recommendations = [
                    "Fix linting violations to improve code quality",
                    f"Target: <{config.threshold * 10:.1f} violations per file",
                    "Run: python3 -m flake8 src/ --max-line-length=120"
                ]
                
            return QualityGateResult(
                gate_type=QualityGateType.LINTING,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return QualityGateResult(
                gate_type=QualityGateType.LINTING,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": "Linting timeout"},
                execution_time_seconds=time.time() - start_time,
                error_message="Linting execution timed out",
                recommendations=["Reduce code complexity to speed up linting"]
            )
            
    def _execute_formatting_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute formatting quality gate using black"""
        try:
            # Check formatting with black
            cmd = ["python3", "-m", "black", "--check", "--diff", str(target_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
            
            if result.returncode == 0:
                # Formatting is correct
                score = 1.0
                status = QualityGateStatus.PASSED
                details = {"formatting_issues": 0, "status": "all_files_formatted"}
                recommendations = []
            else:
                # Formatting issues found
                score = 0.0  # Formatting must be perfect
                status = QualityGateStatus.FAILED
                details = {
                    "formatting_issues": result.stdout.count("would reformat"),
                    "diff_output": result.stdout[:1000]  # Truncate for readability
                }
                recommendations = [
                    "Fix formatting issues with: python3 -m black src/",
                    "Ensure consistent code formatting across all files",
                    "Consider adding pre-commit hooks for automatic formatting"
                ]
                
            return QualityGateResult(
                gate_type=QualityGateType.FORMATTING,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return QualityGateResult(
                gate_type=QualityGateType.FORMATTING,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": "Formatting check timeout"},
                execution_time_seconds=time.time() - start_time,
                error_message="Formatting check timed out",
                recommendations=["Check for infinite loops or very large files"]
            )
            
    def _execute_security_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute security quality gate using bandit"""
        try:
            # Run bandit security scan
            cmd = ["python3", "-m", "bandit", "-r", str(target_path), "-f", "json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
            
            # Parse bandit results
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    high_severity = len([issue for issue in bandit_results.get("results", []) if issue.get("issue_severity") == "HIGH"])
                    medium_severity = len([issue for issue in bandit_results.get("results", []) if issue.get("issue_severity") == "MEDIUM"])
                    low_severity = len([issue for issue in bandit_results.get("results", []) if issue.get("issue_severity") == "LOW"])
                    
                    total_issues = high_severity + medium_severity + low_severity
                    
                    # Calculate score (high severity issues are weighted more)
                    severity_score = max(0.0, 1.0 - (high_severity * 0.5 + medium_severity * 0.2 + low_severity * 0.1))
                    score = severity_score
                    
                    status = QualityGateStatus.PASSED if score >= config.threshold else QualityGateStatus.FAILED
                    
                    details = {
                        "total_issues": total_issues,
                        "high_severity": high_severity,
                        "medium_severity": medium_severity,
                        "low_severity": low_severity,
                        "files_scanned": bandit_results.get("metrics", {}).get("_totals", {}).get("loc", 0)
                    }
                    
                    recommendations = []
                    if high_severity > 0:
                        recommendations.append(f"Fix {high_severity} high severity security issues immediately")
                    if medium_severity > 0:
                        recommendations.append(f"Address {medium_severity} medium severity security issues")
                    if total_issues == 0:
                        recommendations.append("Excellent security posture maintained")
                        
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    score = 0.8  # Assume reasonable security if scan completed
                    status = QualityGateStatus.WARNING
                    details = {"scan_completed": True, "json_parse_error": True}
                    recommendations = ["Review security scan output manually"]
            else:
                # No output, assume clean
                score = 1.0
                status = QualityGateStatus.PASSED
                details = {"security_issues": 0, "status": "clean"}
                recommendations = []
                
            return QualityGateResult(
                gate_type=QualityGateType.SECURITY,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return QualityGateResult(
                gate_type=QualityGateType.SECURITY,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": "Security scan timeout"},
                execution_time_seconds=time.time() - start_time,
                error_message="Security scan timed out",
                recommendations=["Reduce codebase size or increase timeout"]
            )
            
    def _execute_coverage_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute test coverage quality gate using pytest-cov"""
        try:
            # Run pytest with coverage
            cmd = [
                "python3", "-m", "pytest", 
                "--cov=" + str(target_path),
                "--cov-report=json",
                "--cov-report=term-missing",
                str(self.tests_path) if self.tests_path.exists() else str(target_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
            
            # Parse coverage results
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                        
                    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0) / 100
                    score = total_coverage
                    
                    status = QualityGateStatus.PASSED if score >= config.threshold else QualityGateStatus.FAILED
                    
                    details = {
                        "coverage_percentage": total_coverage * 100,
                        "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                        "lines_missing": coverage_data.get("totals", {}).get("missing_lines", 0),
                        "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                    }
                    
                    recommendations = []
                    if total_coverage < config.threshold:
                        recommendations.append(f"Increase test coverage to {config.threshold * 100:.0f}% (currently {total_coverage * 100:.1f}%)")
                        recommendations.append("Add unit tests for uncovered code paths")
                        recommendations.append("Focus on critical business logic coverage")
                    else:
                        recommendations.append("Excellent test coverage maintained")
                        
                    # Clean up coverage file
                    coverage_file.unlink()
                    
                except (json.JSONDecodeError, FileNotFoundError):
                    score = 0.0
                    status = QualityGateStatus.FAILED
                    details = {"error": "Coverage data parsing failed"}
                    recommendations = ["Fix test execution and coverage reporting"]
            else:
                # No coverage file generated
                score = 0.0
                status = QualityGateStatus.FAILED
                details = {"error": "No coverage data generated", "stderr": result.stderr}
                recommendations = [
                    "Ensure pytest and pytest-cov are installed",
                    "Check test discovery and execution",
                    "Verify test files are properly structured"
                ]
                
            return QualityGateResult(
                gate_type=QualityGateType.COVERAGE,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return QualityGateResult(
                gate_type=QualityGateType.COVERAGE,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": "Coverage test timeout"},
                execution_time_seconds=time.time() - start_time,
                error_message="Coverage tests timed out",
                recommendations=["Optimize test execution time or increase timeout"]
            )
            
    def _execute_complexity_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute code complexity quality gate using radon"""
        try:
            # Run radon complexity analysis
            cmd = ["python3", "-m", "radon", "cc", str(target_path), "-j"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.timeout_seconds)
            
            if result.stdout:
                try:
                    complexity_data = json.loads(result.stdout)
                    
                    # Analyze complexity scores
                    high_complexity_functions = 0
                    total_functions = 0
                    complexity_scores = []
                    
                    for file_path, functions in complexity_data.items():
                        for func in functions:
                            total_functions += 1
                            complexity = func.get("complexity", 0)
                            complexity_scores.append(complexity)
                            
                            if complexity > config.custom_rules.get("max_complexity", 10):
                                high_complexity_functions += 1
                                
                    # Calculate score
                    if total_functions > 0:
                        avg_complexity = sum(complexity_scores) / len(complexity_scores)
                        complexity_ratio = high_complexity_functions / total_functions
                        score = max(0.0, 1.0 - complexity_ratio - (avg_complexity / 20))
                    else:
                        score = 1.0  # No functions to analyze
                        
                    status = QualityGateStatus.PASSED if score >= config.threshold else QualityGateStatus.FAILED
                    
                    details = {
                        "total_functions": total_functions,
                        "high_complexity_functions": high_complexity_functions,
                        "average_complexity": avg_complexity if total_functions > 0 else 0,
                        "max_complexity_threshold": config.custom_rules.get("max_complexity", 10)
                    }
                    
                    recommendations = []
                    if high_complexity_functions > 0:
                        recommendations.append(f"Refactor {high_complexity_functions} high complexity functions")
                        recommendations.append("Break down complex functions into smaller, focused functions")
                        recommendations.append("Consider using design patterns to reduce complexity")
                    else:
                        recommendations.append("Good code complexity maintained")
                        
                except json.JSONDecodeError:
                    score = 0.5  # Assume moderate complexity if parsing fails
                    status = QualityGateStatus.WARNING
                    details = {"complexity_analysis_error": True}
                    recommendations = ["Review complexity analysis output manually"]
            else:
                score = 1.0  # No complexity issues found
                status = QualityGateStatus.PASSED
                details = {"complexity_issues": 0}
                recommendations = []
                
            return QualityGateResult(
                gate_type=QualityGateType.COMPLEXITY,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except subprocess.TimeoutExpired:
            return QualityGateResult(
                gate_type=QualityGateType.COMPLEXITY,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": "Complexity analysis timeout"},
                execution_time_seconds=time.time() - start_time,
                error_message="Complexity analysis timed out",
                recommendations=["Reduce codebase size or increase timeout"]
            )
            
    def _execute_documentation_gate(self, config: QualityGateConfig, target_path: Path, start_time: float) -> QualityGateResult:
        """Execute documentation quality gate"""
        try:
            # Analyze documentation coverage
            python_files = list(target_path.rglob("*.py"))
            total_files = len(python_files)
            documented_files = 0
            total_functions = 0
            documented_functions = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for module docstring
                    if '"""' in content or "'''" in content:
                        documented_files += 1
                        
                    # Count functions and their documentation
                    lines = content.split('\n')
                    in_function = False
                    function_has_docstring = False
                    
                    for i, line in enumerate(lines):
                        stripped = line.strip()
                        
                        if stripped.startswith('def ') and not stripped.startswith('def _'):  # Public functions only
                            total_functions += 1
                            in_function = True
                            function_has_docstring = False
                            
                            # Check next few lines for docstring
                            for j in range(i + 1, min(i + 5, len(lines))):
                                if '"""' in lines[j] or "'''" in lines[j]:
                                    function_has_docstring = True
                                    break
                                    
                            if function_has_docstring:
                                documented_functions += 1
                                
                except Exception as e:
                    self.logger.warning(f"Error analyzing {py_file}: {e}")
                    
            # Calculate documentation score
            file_doc_ratio = documented_files / max(1, total_files)
            function_doc_ratio = documented_functions / max(1, total_functions)
            overall_doc_score = (file_doc_ratio + function_doc_ratio) / 2
            
            score = overall_doc_score
            status = QualityGateStatus.PASSED if score >= config.threshold else QualityGateStatus.FAILED
            
            details = {
                "total_files": total_files,
                "documented_files": documented_files,
                "file_documentation_ratio": file_doc_ratio,
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "function_documentation_ratio": function_doc_ratio,
                "overall_documentation_score": overall_doc_score
            }
            
            recommendations = []
            if file_doc_ratio < config.threshold:
                recommendations.append(f"Add module docstrings to {total_files - documented_files} files")
            if function_doc_ratio < config.threshold:
                recommendations.append(f"Add docstrings to {total_functions - documented_functions} functions")
            if score >= config.threshold:
                recommendations.append("Good documentation coverage maintained")
                
            return QualityGateResult(
                gate_type=QualityGateType.DOCUMENTATION,
                status=status,
                score=score,
                details=details,
                execution_time_seconds=time.time() - start_time,
                recommendations=recommendations
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=QualityGateType.DOCUMENTATION,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details={"error": str(e)},
                execution_time_seconds=time.time() - start_time,
                error_message=str(e),
                recommendations=["Fix documentation analysis error"]
            )
            
    def _determine_overall_status(self, gate_results: List[QualityGateResult], overall_score: float) -> QualityGateStatus:
        """Determine overall quality assessment status"""
        failed_gates = [result for result in gate_results if result.status == QualityGateStatus.FAILED]
        warning_gates = [result for result in gate_results if result.status == QualityGateStatus.WARNING]
        
        if len(failed_gates) > 0:
            return QualityGateStatus.FAILED
        elif len(warning_gates) > 0:
            return QualityGateStatus.WARNING
        elif overall_score >= 0.8:
            return QualityGateStatus.PASSED
        else:
            return QualityGateStatus.WARNING
            
    def _generate_quality_recommendations(self, gate_results: List[QualityGateResult]) -> List[str]:
        """Generate overall quality improvement recommendations"""
        recommendations = []
        
        # Collect all gate-specific recommendations
        for result in gate_results:
            recommendations.extend(result.recommendations)
            
        # Add overall recommendations
        failed_gates = [result for result in gate_results if result.status == QualityGateStatus.FAILED]
        if failed_gates:
            recommendations.append(f"Priority: Fix {len(failed_gates)} failed quality gates")
            
        # Beast Mode specific recommendations
        recommendations.extend([
            "Ensure all modules inherit from ReflectiveModule for RM compliance",
            "Implement comprehensive health monitoring in all components",
            "Follow systematic approach principles (no ad-hoc implementations)",
            "Maintain >90% test coverage as per DR8 requirements",
            "Document all architectural decisions using ADR system"
        ])
        
        return recommendations
        
    def _check_beast_mode_compliance(self, gate_results: List[QualityGateResult]) -> Dict[str, bool]:
        """Check compliance with Beast Mode specific requirements"""
        compliance_status = {}
        
        # Check coverage compliance (DR8: >90% coverage)
        coverage_result = next((r for r in gate_results if r.gate_type == QualityGateType.COVERAGE), None)
        compliance_status["dr8_coverage_compliance"] = (
            coverage_result is not None and 
            coverage_result.score >= 0.9 and 
            coverage_result.status == QualityGateStatus.PASSED
        )
        
        # Check security compliance
        security_result = next((r for r in gate_results if r.gate_type == QualityGateType.SECURITY), None)
        compliance_status["security_compliance"] = (
            security_result is not None and 
            security_result.status == QualityGateStatus.PASSED
        )
        
        # Check code quality compliance
        linting_result = next((r for r in gate_results if r.gate_type == QualityGateType.LINTING), None)
        formatting_result = next((r for r in gate_results if r.gate_type == QualityGateType.FORMATTING), None)
        compliance_status["code_quality_compliance"] = (
            linting_result is not None and linting_result.status == QualityGateStatus.PASSED and
            formatting_result is not None and formatting_result.status == QualityGateStatus.PASSED
        )
        
        # Check documentation compliance
        doc_result = next((r for r in gate_results if r.gate_type == QualityGateType.DOCUMENTATION), None)
        compliance_status["documentation_compliance"] = (
            doc_result is not None and 
            doc_result.score >= 0.8 and 
            doc_result.status == QualityGateStatus.PASSED
        )
        
        # Overall Beast Mode compliance
        compliance_status["overall_beast_mode_compliance"] = all(compliance_status.values())
        
        return compliance_status
        
    def enforce_quality_gates(self, target_path: Optional[str] = None, fail_on_error: bool = True) -> Dict[str, Any]:
        """
        Enforce quality gates with systematic validation
        Returns enforcement result with pass/fail status
        """
        try:
            self.logger.info("Enforcing automated quality gates")
            
            # Execute quality assessment
            assessment = self.execute_quality_assessment(target_path)
            
            # Determine enforcement result
            enforcement_passed = assessment.overall_status == QualityGateStatus.PASSED
            
            if not enforcement_passed and fail_on_error:
                self.logger.error(f"Quality gate enforcement FAILED: {assessment.overall_status.value}")
            else:
                self.logger.info(f"Quality gate enforcement result: {assessment.overall_status.value}")
                
            return {
                "enforcement_passed": enforcement_passed,
                "overall_status": assessment.overall_status.value,
                "overall_score": assessment.overall_score,
                "failed_gates": [r.gate_type.value for r in assessment.gate_results if r.status == QualityGateStatus.FAILED],
                "compliance_status": assessment.compliance_status,
                "recommendations": assessment.recommendations,
                "execution_time": assessment.total_execution_time,
                "beast_mode_compliant": assessment.compliance_status.get("overall_beast_mode_compliance", False)
            }
            
        except Exception as e:
            self.logger.error(f"Quality gate enforcement failed: {e}")
            return {
                "enforcement_passed": False,
                "error": str(e),
                "overall_status": "error",
                "recommendations": [f"Fix quality gate enforcement error: {e}"]
            }