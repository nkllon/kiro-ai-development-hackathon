#!/usr/bin/env python3
"""
Systematic Failure Mode Detector
===============================

Comprehensive failure mode detection and analysis system for the Beast Mode framework.
Addresses the identified systemic failure modes:
- Dquote errors in command execution
- CLI availability and timeout issues
- Missing requirements validation
- RMDDD integration failures
- General timeout and execution failures

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Systematic failure detection and recovery
"""

import sys
import os
import time
import subprocess
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
import re
import signal
from pathlib import Path


class FailureMode(Enum):
    """Critical failure modes identified in the system."""

    DQUOTE_ERROR = "dquote_error"
    CLI_UNAVAILABLE = "cli_unavailable"
    CLI_TIMEOUT = "cli_timeout"
    REQUIREMENTS_MISSING = "requirements_missing"
    RMDDD_FAILURE = "rmddd_failure"
    EXECUTION_TIMEOUT = "execution_timeout"
    SUBPROCESS_BLOCKING = "subprocess_blocking"
    AUTHORIZATION_FAILURE = "authorization_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN_ERROR = "unknown_error"


class FailureSeverity(Enum):
    """Failure severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FailureContext:
    """Context information for failure analysis."""

    failure_mode: FailureMode
    severity: FailureSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    component: str = ""
    operation: str = ""
    error_message: str = ""
    stack_trace: str = ""
    environment: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    is_recoverable: bool = True


@dataclass
class FailureAnalysis:
    """Comprehensive failure analysis result."""

    failure_id: str
    context: FailureContext
    root_causes: List[str]
    impact_assessment: Dict[str, Any]
    recovery_strategies: List[str]
    prevention_measures: List[str]
    is_systemic: bool
    confidence_score: float


class SystematicFailureDetector:
    """
    Systematic failure detection and analysis system.

    Provides comprehensive failure mode detection, analysis, and recovery
    for the Beast Mode framework.
    """

    def __init__(self):
        """Initialize the failure detector."""
        self.failure_history: List[FailureAnalysis] = []
        self.active_failures: Dict[str, FailureContext] = {}
        self.recovery_strategies: Dict[FailureMode, List[str]] = (
            self._initialize_recovery_strategies()
        )
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for failure detection."""
        logger = logging.getLogger("systematic_failure_detector")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_recovery_strategies(self) -> Dict[FailureMode, List[str]]:
        """Initialize recovery strategies for each failure mode."""
        return {
            FailureMode.DQUOTE_ERROR: [
                "Validate command syntax before execution",
                "Use proper shell escaping mechanisms",
                "Implement command sanitization",
                "Provide alternative execution paths",
            ],
            FailureMode.CLI_UNAVAILABLE: [
                "Check CLI installation and PATH",
                "Provide CLI installation instructions",
                "Implement fallback execution methods",
                "Use alternative tools when available",
            ],
            FailureMode.CLI_TIMEOUT: [
                "Implement proper timeout handling",
                "Use non-blocking execution patterns",
                "Provide progress indicators",
                "Implement retry logic with backoff",
            ],
            FailureMode.REQUIREMENTS_MISSING: [
                "Validate requirements before execution",
                "Provide requirements generation tools",
                "Implement requirements discovery",
                "Generate requirements from existing code",
            ],
            FailureMode.RMDDD_FAILURE: [
                "Validate RMDDD integration",
                "Check RMDDD service availability",
                "Implement RMDDD health checks",
                "Provide RMDDD setup assistance",
            ],
            FailureMode.EXECUTION_TIMEOUT: [
                "Implement timeout protection",
                "Use safe execution patterns",
                "Provide process termination",
                "Implement resource monitoring",
            ],
            FailureMode.SUBPROCESS_BLOCKING: [
                "Use timeout-protected subprocess calls",
                "Implement process monitoring",
                "Provide manual termination options",
                "Use non-blocking execution patterns",
            ],
            FailureMode.AUTHORIZATION_FAILURE: [
                "Validate authorization tokens",
                "Implement token refresh mechanisms",
                "Provide clear error messages",
                "Implement privilege checking",
            ],
            FailureMode.RESOURCE_EXHAUSTION: [
                "Monitor resource usage",
                "Implement resource limits",
                "Provide resource cleanup",
                "Implement graceful degradation",
            ],
            FailureMode.UNKNOWN_ERROR: [
                "Implement comprehensive logging",
                "Provide error context capture",
                "Implement fallback mechanisms",
                "Request user assistance",
            ],
        }

    def detect_dquote_error(self, command: str, error_output: str) -> bool:
        """Detect dquote errors in command execution."""
        dquote_patterns = [
            r"unexpected EOF while looking for matching",
            r"unterminated quoted string",
            r"syntax error near unexpected token",
            r"bash: unexpected EOF",
            r"zsh: parse error",
        ]

        for pattern in dquote_patterns:
            if re.search(pattern, error_output, re.IGNORECASE):
                return True

        return False

    def detect_cli_availability(self, command: str) -> Tuple[bool, str]:
        """Detect CLI availability and issues."""
        try:
            # Check if command exists
            result = subprocess.run(
                ["which", command.split()[0]], capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                return False, f"CLI '{command.split()[0]}' not found in PATH"

            # Check if command is executable
            if not os.access(result.stdout.strip(), os.X_OK):
                return False, f"CLI '{command.split()[0]}' is not executable"

            return True, "CLI available"

        except subprocess.TimeoutExpired:
            return False, "CLI availability check timed out"
        except Exception as e:
            return False, f"CLI availability check failed: {e}"

    def detect_timeout_issues(self, start_time: datetime, timeout_seconds: int) -> bool:
        """Detect if operation has exceeded timeout."""
        elapsed = (datetime.now() - start_time).total_seconds()
        return elapsed > timeout_seconds

    def detect_requirements_missing(self, operation: str) -> bool:
        """Detect missing requirements for operations."""
        # Check for common requirement patterns
        requirement_patterns = [
            r"requirements\.txt",
            r"pyproject\.toml",
            r"package\.json",
            r"requirements\.yml",
            r"environment\.yml",
        ]

        for pattern in requirement_patterns:
            if re.search(pattern, operation, re.IGNORECASE):
                # Check if file exists
                if not os.path.exists(pattern):
                    return True

        return False

    def detect_rmddd_failure(self, operation: str, error_output: str) -> bool:
        """Detect RMDDD integration failures."""
        rmddd_failure_patterns = [
            r"rmddd.*not found",
            r"rmddd.*failed",
            r"rmddd.*error",
            r"reflective.*module.*error",
            r"domain.*driven.*design.*error",
        ]

        for pattern in rmddd_failure_patterns:
            if re.search(pattern, error_output, re.IGNORECASE):
                return True

        return False

    def analyze_failure(
        self, error: Exception, context: Dict[str, Any]
    ) -> FailureAnalysis:
        """Perform comprehensive failure analysis."""
        failure_id = f"failure_{int(time.time())}_{len(self.failure_history)}"

        # Determine failure mode
        failure_mode = self._classify_failure_mode(error, context)

        # Create failure context
        failure_context = FailureContext(
            failure_mode=failure_mode,
            severity=self._assess_severity(failure_mode, context),
            component=context.get("component", "unknown"),
            operation=context.get("operation", "unknown"),
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            environment=context.get("environment", {}),
        )

        # Analyze root causes
        root_causes = self._analyze_root_causes(failure_context)

        # Assess impact
        impact_assessment = self._assess_impact(failure_context)

        # Get recovery strategies
        recovery_strategies = self.recovery_strategies.get(failure_mode, [])

        # Determine prevention measures
        prevention_measures = self._determine_prevention_measures(failure_context)

        # Check if systemic
        is_systemic = self._check_systemic_failure(failure_context)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            failure_context, root_causes
        )

        analysis = FailureAnalysis(
            failure_id=failure_id,
            context=failure_context,
            root_causes=root_causes,
            impact_assessment=impact_assessment,
            recovery_strategies=recovery_strategies,
            prevention_measures=prevention_measures,
            is_systemic=is_systemic,
            confidence_score=confidence_score,
        )

        # Store analysis
        self.failure_history.append(analysis)
        self.active_failures[failure_id] = failure_context

        return analysis

    def _classify_failure_mode(
        self, error: Exception, context: Dict[str, Any]
    ) -> FailureMode:
        """Classify the failure mode based on error and context."""
        error_str = str(error).lower()
        context_str = str(context).lower()

        # Check for specific failure modes
        if isinstance(error, subprocess.TimeoutExpired):
            return FailureMode.EXECUTION_TIMEOUT
        elif isinstance(error, subprocess.CalledProcessError):
            if self.detect_dquote_error(context.get("command", ""), error_str):
                return FailureMode.DQUOTE_ERROR
            elif self.detect_rmddd_failure(context.get("operation", ""), error_str):
                return FailureMode.RMDDD_FAILURE
            else:
                return FailureMode.SUBPROCESS_BLOCKING
        elif "permission denied" in error_str or "access denied" in error_str:
            return FailureMode.AUTHORIZATION_FAILURE
        elif "resource" in error_str and (
            "exhausted" in error_str or "limit" in error_str
        ):
            return FailureMode.RESOURCE_EXHAUSTION
        elif "requirements" in context_str and "missing" in context_str:
            return FailureMode.REQUIREMENTS_MISSING
        elif "cli" in context_str and (
            "not found" in error_str or "unavailable" in error_str
        ):
            return FailureMode.CLI_UNAVAILABLE
        else:
            return FailureMode.UNKNOWN_ERROR

    def _assess_severity(
        self, failure_mode: FailureMode, context: Dict[str, Any]
    ) -> FailureSeverity:
        """Assess failure severity."""
        severity_map = {
            FailureMode.DQUOTE_ERROR: FailureSeverity.MEDIUM,
            FailureMode.CLI_UNAVAILABLE: FailureSeverity.HIGH,
            FailureMode.CLI_TIMEOUT: FailureSeverity.MEDIUM,
            FailureMode.REQUIREMENTS_MISSING: FailureSeverity.HIGH,
            FailureMode.RMDDD_FAILURE: FailureSeverity.HIGH,
            FailureMode.EXECUTION_TIMEOUT: FailureSeverity.CRITICAL,
            FailureMode.SUBPROCESS_BLOCKING: FailureSeverity.CRITICAL,
            FailureMode.AUTHORIZATION_FAILURE: FailureSeverity.HIGH,
            FailureMode.RESOURCE_EXHAUSTION: FailureSeverity.CRITICAL,
            FailureMode.UNKNOWN_ERROR: FailureSeverity.MEDIUM,
        }

        return severity_map.get(failure_mode, FailureSeverity.MEDIUM)

    def _analyze_root_causes(self, context: FailureContext) -> List[str]:
        """Analyze root causes of the failure."""
        root_causes = []

        if context.failure_mode == FailureMode.DQUOTE_ERROR:
            root_causes.extend(
                [
                    "Improper shell command escaping",
                    "Missing quote validation",
                    "Incomplete command syntax",
                ]
            )
        elif context.failure_mode == FailureMode.CLI_UNAVAILABLE:
            root_causes.extend(
                ["CLI not installed", "PATH configuration issue", "Permission problems"]
            )
        elif context.failure_mode == FailureMode.EXECUTION_TIMEOUT:
            root_causes.extend(
                [
                    "Missing timeout protection",
                    "Resource constraints",
                    "Infinite loops or deadlocks",
                ]
            )
        elif context.failure_mode == FailureMode.REQUIREMENTS_MISSING:
            root_causes.extend(
                [
                    "Incomplete requirements analysis",
                    "Missing requirements validation",
                    "Inadequate setup procedures",
                ]
            )
        elif context.failure_mode == FailureMode.RMDDD_FAILURE:
            root_causes.extend(
                [
                    "RMDDD service unavailable",
                    "Integration configuration issues",
                    "Service dependency failures",
                ]
            )

        return root_causes

    def _assess_impact(self, context: FailureContext) -> Dict[str, Any]:
        """Assess the impact of the failure."""
        impact = {
            "severity": context.severity.value,
            "component_affected": context.component,
            "operation_blocked": context.operation,
            "system_wide": context.severity == FailureSeverity.CRITICAL,
            "recovery_time_estimate": self._estimate_recovery_time(context),
            "user_impact": self._assess_user_impact(context),
        }

        return impact

    def _estimate_recovery_time(self, context: FailureContext) -> str:
        """Estimate recovery time for the failure."""
        recovery_time_map = {
            FailureMode.DQUOTE_ERROR: "1-5 minutes",
            FailureMode.CLI_UNAVAILABLE: "5-15 minutes",
            FailureMode.CLI_TIMEOUT: "1-3 minutes",
            FailureMode.REQUIREMENTS_MISSING: "10-30 minutes",
            FailureMode.RMDDD_FAILURE: "15-45 minutes",
            FailureMode.EXECUTION_TIMEOUT: "Immediate",
            FailureMode.SUBPROCESS_BLOCKING: "Immediate",
            FailureMode.AUTHORIZATION_FAILURE: "5-15 minutes",
            FailureMode.RESOURCE_EXHAUSTION: "Immediate",
            FailureMode.UNKNOWN_ERROR: "Variable",
        }

        return recovery_time_map.get(context.failure_mode, "Unknown")

    def _assess_user_impact(self, context: FailureContext) -> str:
        """Assess user impact of the failure."""
        if context.severity == FailureSeverity.CRITICAL:
            return "Complete system unavailability"
        elif context.severity == FailureSeverity.HIGH:
            return "Major functionality affected"
        elif context.severity == FailureSeverity.MEDIUM:
            return "Some functionality affected"
        else:
            return "Minimal impact"

    def _determine_prevention_measures(self, context: FailureContext) -> List[str]:
        """Determine prevention measures for the failure."""
        prevention_measures = []

        if context.failure_mode == FailureMode.DQUOTE_ERROR:
            prevention_measures.extend(
                [
                    "Implement command syntax validation",
                    "Use proper shell escaping libraries",
                    "Add command sanitization",
                ]
            )
        elif context.failure_mode == FailureMode.CLI_UNAVAILABLE:
            prevention_measures.extend(
                [
                    "Implement CLI availability checks",
                    "Provide installation validation",
                    "Add fallback execution methods",
                ]
            )
        elif context.failure_mode == FailureMode.EXECUTION_TIMEOUT:
            prevention_measures.extend(
                [
                    "Implement timeout protection for all operations",
                    "Add progress monitoring",
                    "Use safe execution patterns",
                ]
            )
        elif context.failure_mode == FailureMode.REQUIREMENTS_MISSING:
            prevention_measures.extend(
                [
                    "Implement requirements validation",
                    "Add requirements discovery",
                    "Provide requirements generation tools",
                ]
            )
        elif context.failure_mode == FailureMode.RMDDD_FAILURE:
            prevention_measures.extend(
                [
                    "Implement RMDDD health checks",
                    "Add service availability monitoring",
                    "Provide integration validation",
                ]
            )

        return prevention_measures

    def _check_systemic_failure(self, context: FailureContext) -> bool:
        """Check if this is a systemic failure."""
        # Count similar failures in history
        similar_failures = [
            f
            for f in self.failure_history
            if f.context.failure_mode == context.failure_mode
            and (context.timestamp - f.context.timestamp).total_seconds()
            < 3600  # 1 hour
        ]

        return len(similar_failures) >= 3  # 3+ similar failures in 1 hour = systemic

    def _calculate_confidence_score(
        self, context: FailureContext, root_causes: List[str]
    ) -> float:
        """Calculate confidence score for the analysis."""
        base_score = 0.7

        # Increase confidence based on specific indicators
        if context.stack_trace and len(context.stack_trace) > 100:
            base_score += 0.1

        if len(root_causes) > 0:
            base_score += 0.1

        if context.error_message and len(context.error_message) > 50:
            base_score += 0.1

        return min(base_score, 1.0)

    def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of all failures."""
        if not self.failure_history:
            return {"total_failures": 0, "message": "No failures detected"}

        failure_counts = {}
        for analysis in self.failure_history:
            mode = analysis.context.failure_mode.value
            failure_counts[mode] = failure_counts.get(mode, 0) + 1

        systemic_failures = [f for f in self.failure_history if f.is_systemic]

        return {
            "total_failures": len(self.failure_history),
            "active_failures": len(self.active_failures),
            "systemic_failures": len(systemic_failures),
            "failure_distribution": failure_counts,
            "most_common_failure": (
                max(failure_counts.items(), key=lambda x: x[1])[0]
                if failure_counts
                else None
            ),
            "average_confidence": sum(f.confidence_score for f in self.failure_history)
            / len(self.failure_history),
        }

    def generate_recovery_report(self) -> str:
        """Generate a comprehensive recovery report."""
        if not self.failure_history:
            return "No failures detected - system is healthy"

        report = []
        report.append("=" * 80)
        report.append("SYSTEMATIC FAILURE DETECTION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        summary = self.get_failure_summary()
        report.append("FAILURE SUMMARY:")
        report.append(f"  Total Failures: {summary['total_failures']}")
        report.append(f"  Active Failures: {summary['active_failures']}")
        report.append(f"  Systemic Failures: {summary['systemic_failures']}")
        report.append(f"  Average Confidence: {summary['average_confidence']:.3f}")
        report.append("")

        if summary["most_common_failure"]:
            report.append(f"MOST COMMON FAILURE: {summary['most_common_failure']}")
            report.append("")

        report.append("FAILURE DISTRIBUTION:")
        for mode, count in summary["failure_distribution"].items():
            report.append(f"  {mode}: {count}")
        report.append("")

        report.append("RECENT FAILURES:")
        for analysis in self.failure_history[-5:]:  # Last 5 failures
            report.append(
                f"  {analysis.failure_id}: {analysis.context.failure_mode.value}"
            )
            report.append(f"    Severity: {analysis.context.severity.value}")
            report.append(f"    Component: {analysis.context.component}")
            report.append(f"    Timestamp: {analysis.context.timestamp}")
            if analysis.is_systemic:
                report.append(f"    ⚠️  SYSTEMIC FAILURE")
            report.append("")

        return "\n".join(report)


def main() -> None:
    """Main function for testing the failure detector."""
    detector = SystematicFailureDetector()

    # Test failure detection
    print("Testing Systematic Failure Detector...")

    # Simulate different failure modes
    test_failures = [
        (
            subprocess.TimeoutExpired("git", 30),
            {"component": "git", "operation": "push"},
        ),
        (
            subprocess.CalledProcessError(1, "bash", "unexpected EOF"),
            {"component": "bash", "operation": "script_execution"},
        ),
        (
            FileNotFoundError("CLI not found"),
            {"component": "cli", "operation": "command_execution"},
        ),
        (
            PermissionError("Access denied"),
            {"component": "auth", "operation": "token_validation"},
        ),
    ]

    for error, context in test_failures:
        analysis = detector.analyze_failure(error, context)
        print(f"\nFailure Analysis: {analysis.failure_id}")
        print(f"  Mode: {analysis.context.failure_mode.value}")
        print(f"  Severity: {analysis.context.severity.value}")
        print(f"  Systemic: {analysis.is_systemic}")
        print(f"  Confidence: {analysis.confidence_score:.3f}")

    # Generate report
    print("\n" + detector.generate_recovery_report())


if __name__ == "__main__":
    main()
