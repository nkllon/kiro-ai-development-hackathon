#!/usr/bin/env python3
"""
Bandit Security Integration - Direct Python API Usage

This module integrates Bandit's security scanning capabilities directly into our
model-driven security system without requiring subprocess calls.

Features:
- Direct Python API integration with Bandit
- AST-based security analysis
- Integration with project model registry
- Customizable security profiles
- Rich reporting and issue management
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from bandit.core import config as bandit_config
    from bandit.core import manager as bandit_manager

    BANDIT_AVAILABLE = True
except ImportError:
    BANDIT_AVAILABLE = False
    logging.warning("Bandit not available - install with: uv add bandit")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Represents a security issue found by Bandit"""

    severity: str
    confidence: str
    issue_type: str
    message: str
    filename: str
    line_number: int
    code: str
    cwe_id: Optional[str] = None
    more_info: Optional[str] = None


@dataclass
class SecurityScanResult:
    """Results from a Bandit security scan"""

    files_scanned: int
    issues_found: int
    issues: list[SecurityIssue]
    metrics: dict[str, Any]
    scan_duration: float
    success: bool
    error_message: Optional[str] = None


class BanditSecurityScanner:
    """Direct integration with Bandit's Python API for security scanning"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the Bandit security scanner

        Args:
            config_file: Optional path to Bandit configuration file
        """
        if not BANDIT_AVAILABLE:
            msg = "Bandit is not available. Install with: uv add bandit"
            raise ImportError(msg)

        self.config_file = config_file
        self.bandit_config = None
        self.bandit_manager = None
        self._initialize_bandit()

    def _initialize_bandit(self):
        """Initialize Bandit configuration and manager"""
        try:
            # Create Bandit configuration
            self.bandit_config = bandit_config.BanditConfig(self.config_file)

            # Create Bandit manager with file aggregation
            self.bandit_manager = bandit_manager.BanditManager(
                config=self.bandit_config,
                agg_type="file",
                debug=False,
                verbose=False,
                quiet=True,
            )

            logger.info("Bandit security scanner initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Bandit: {e}")
            raise

    def scan_file(self, file_path: str) -> SecurityScanResult:
        """Scan a single file for security issues

        Args:
            file_path: Path to the file to scan

        Returns:
            SecurityScanResult with scan results
        """
        if not Path(file_path).exists():
            return SecurityScanResult(
                files_scanned=0,
                issues_found=0,
                issues=[],
                metrics={},
                scan_duration=0.0,
                success=False,
                error_message=f"File not found: {file_path}",
            )

        try:
            import time

            start_time = time.time()

            # Configure manager for single file scan
            self.bandit_manager.files_list = [file_path]
            self.bandit_manager.skipped = []

            # Run security scan
            self.bandit_manager.run_tests()

            # Collect results
            issues = self._collect_issues()
            metrics = self._collect_metrics()

            scan_duration = time.time() - start_time

            return SecurityScanResult(
                files_scanned=1,
                issues_found=len(issues),
                issues=issues,
                metrics=metrics,
                scan_duration=scan_duration,
                success=True,
            )

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return SecurityScanResult(
                files_scanned=0,
                issues_found=0,
                issues=[],
                metrics={},
                scan_duration=0.0,
                success=False,
                error_message=str(e),
            )

    def scan_directory(self, directory_path: str, file_patterns: Optional[list[str]] = None) -> SecurityScanResult:
        """Scan a directory for security issues

        Args:
            directory_path: Path to directory to scan
            file_patterns: Optional list of file patterns to include

        Returns:
            SecurityScanResult with scan results
        """
        if not Path(directory_path).exists():
            return SecurityScanResult(
                files_scanned=0,
                issues_found=0,
                issues=[],
                metrics={},
                scan_duration=0.0,
                success=False,
                error_message=f"Directory not found: {directory_path}",
            )

        try:
            import time

            start_time = time.time()

            # Find Python files to scan
            if file_patterns is None:
                file_patterns = ["*.py"]

            files_to_scan = []
            for pattern in file_patterns:
                files_to_scan.extend(Path(directory_path).glob(pattern))

            if not files_to_scan:
                return SecurityScanResult(
                    files_scanned=0,
                    issues_found=0,
                    issues=[],
                    metrics={},
                    scan_duration=0.0,
                    success=True,
                    error_message="No matching files found",
                )

            # Configure manager for directory scan
            self.bandit_manager.files_list = [str(f) for f in files_to_scan]
            self.bandit_manager.skipped = []

            # Run security scan
            self.bandit_manager.run_tests()

            # Collect results
            issues = self._collect_issues()
            metrics = self._collect_metrics()

            scan_duration = time.time() - start_time

            return SecurityScanResult(
                files_scanned=len(files_to_scan),
                issues_found=len(issues),
                issues=issues,
                metrics=metrics,
                scan_duration=scan_duration,
                success=True,
            )

        except Exception as e:
            logger.error(f"Error scanning directory {directory_path}: {e}")
            return SecurityScanResult(
                files_scanned=0,
                issues_found=0,
                issues=[],
                metrics={},
                scan_duration=0.0,
                success=False,
                error_message=str(e),
            )

    def _collect_issues(self) -> list[SecurityIssue]:
        """Collect security issues from Bandit manager"""
        issues = []

        try:
            # Get issues from manager
            issue_list = self.bandit_manager.get_issue_list()

            for issue in issue_list:
                security_issue = SecurityIssue(
                    severity=(issue.severity.name if hasattr(issue.severity, "name") else str(issue.severity)),
                    confidence=(issue.confidence.name if hasattr(issue.confidence, "name") else str(issue.confidence)),
                    issue_type=issue.test_id,
                    message=issue.text,
                    filename=issue.fname,
                    line_number=issue.lineno,
                    code=issue.get_code(),
                    cwe_id=getattr(issue, "cwe", None),
                    more_info=None,
                )
                issues.append(security_issue)

        except Exception as e:
            logger.error(f"Error collecting issues: {e}")

        return issues

    def _collect_metrics(self) -> dict[str, Any]:
        """Collect metrics from Bandit manager"""
        metrics = {}

        try:
            if hasattr(self.bandit_manager, "metrics"):
                # Extract relevant metrics
                metrics = {
                    "total_lines": getattr(self.bandit_manager.metrics, "total_lines", 0),
                    "skipped_files": len(self.bandit_manager.skipped),
                    "scanned_files": len(self.bandit_manager.files_list),
                }
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        return metrics

    def get_security_profile(self) -> dict[str, Any]:
        """Get current security profile configuration"""
        if self.bandit_config and hasattr(self.bandit_config, "_config"):
            return self.bandit_config._config.copy()
        return {}

    def update_security_profile(self, profile_updates: dict[str, Any]):
        """Update security profile configuration

        Args:
            profile_updates: Dictionary of profile updates
        """
        if self.bandit_config and hasattr(self.bandit_config, "_config"):
            self.bandit_config._config.update(profile_updates)
            logger.info("Security profile updated")
        else:
            logger.warning("Cannot update security profile - config not available")


class ModelDrivenSecurityScanner:
    """Integrates Bandit with our project model registry for intelligent security scanning"""

    def __init__(self, project_model_path: str = "project_model_registry.json"):
        """Initialize the model-driven security scanner

        Args:
            project_model_path: Path to project model registry
        """
        self.project_model_path = Path(project_model_path)
        self.project_model = self._load_project_model()
        self.bandit_scanner = BanditSecurityScanner()

    def _load_project_model(self) -> dict[str, Any]:
        """Load the project model registry"""
        try:
            with open(self.project_model_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project model: {e}")
            return {}

    def scan_project(self, target_paths: Optional[list[str]] = None) -> SecurityScanResult:
        """Scan the project based on model-driven configuration

        Args:
            target_paths: Optional list of specific paths to scan

        Returns:
            SecurityScanResult with comprehensive scan results
        """
        if not target_paths:
            target_paths = self._get_default_scan_paths()

        logger.info(f"Starting model-driven security scan of {len(target_paths)} paths")

        all_issues = []
        total_files = 0
        total_duration = 0.0

        for path in target_paths:
            path_obj = Path(path)

            if path_obj.is_file():
                result = self.bandit_scanner.scan_file(path)
                all_issues.extend(result.issues)
                total_files += result.files_scanned
                total_duration += result.scan_duration

            elif path_obj.is_dir():
                result = self.bandit_scanner.scan_directory(path)
                all_issues.extend(result.issues)
                total_files += result.files_scanned
                total_duration += result.scan_duration

        # Aggregate results
        return SecurityScanResult(
            files_scanned=total_files,
            issues_found=len(all_issues),
            issues=all_issues,
            metrics={"total_duration": total_duration},
            scan_duration=total_duration,
            success=True,
        )

    def _get_default_scan_paths(self) -> list[str]:
        """Get default scan paths based on project model"""
        default_paths = []

        # Add common source directories
        common_dirs = ["src", "app", "lib", "scripts", "tests"]
        for dir_name in common_dirs:
            if Path(dir_name).exists():
                default_paths.append(dir_name)

        # Add root Python files
        for py_file in Path().glob("*.py"):
            default_paths.append(str(py_file))

        return default_paths

    def generate_security_report(self, scan_result: SecurityScanResult) -> str:
        """Generate a human-readable security report

        Args:
            scan_result: Results from security scan

        Returns:
            Formatted security report string
        """
        if not scan_result.success:
            return f"Security scan failed: {scan_result.error_message}"

        report_lines = [
            "🔒 Security Scan Report",
            "=" * 50,
            f"Files Scanned: {scan_result.files_scanned}",
            f"Issues Found: {scan_result.issues_found}",
            f"Scan Duration: {scan_result.scan_duration:.2f}s",
            "",
            "📊 Issue Summary:",
        ]

        if scan_result.issues:
            # Group issues by severity
            severity_groups = {}
            for issue in scan_result.issues:
                severity = issue.severity
                if severity not in severity_groups:
                    severity_groups[severity] = []
                severity_groups[severity].append(issue)

            for severity in ["HIGH", "MEDIUM", "LOW"]:
                if severity in severity_groups:
                    issues = severity_groups[severity]
                    report_lines.append(f"\n{severity} Severity ({len(issues)} issues):")
                    for issue in issues[:5]:  # Show first 5 of each severity
                        report_lines.append(f"  • {issue.issue_type}: {issue.message}")
                        report_lines.append(f"    File: {issue.filename}:{issue.line_number}")
                    if len(issues) > 5:
                        report_lines.append(f"    ... and {len(issues) - 5} more")
        else:
            report_lines.append("✅ No security issues found!")

        return "\n".join(report_lines)

    def export_results_json(self, scan_result: SecurityScanResult, output_path: str):
        """Export scan results to JSON file

        Args:
            scan_result: Results from security scan
            output_path: Path to output JSON file
        """
        try:
            # Convert dataclass to dict for JSON serialization
            result_dict = asdict(scan_result)

            with open(output_path, "w") as f:
                json.dump(result_dict, f, indent=2, default=str)

            logger.info(f"Security scan results exported to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export results: {e}")


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Model-driven security scanning with Bandit")
    parser.add_argument("--path", "-p", help="Path to scan (file or directory)")
    parser.add_argument("--project", action="store_true", help="Scan entire project based on model")
    parser.add_argument("--output", "-o", help="Output JSON file for results")
    parser.add_argument("--report", "-r", action="store_true", help="Generate human-readable report")

    args = parser.parse_args()

    try:
        if args.project:
            # Project-wide scan
            scanner = ModelDrivenSecurityScanner()
            result = scanner.scan_project()

            if args.report:
                print(scanner.generate_security_report(result))

            if args.output:
                scanner.export_results_json(result, args.output)

        elif args.path:
            # Single path scan
            bandit_scanner = BanditSecurityScanner()
            path_obj = Path(args.path)

            if path_obj.is_file():
                result = bandit_scanner.scan_file(args.path)
            else:
                result = bandit_scanner.scan_directory(args.path)

            if args.report:
                # Create temporary scanner for report generation
                temp_scanner = ModelDrivenSecurityScanner()
                print(temp_scanner.generate_security_report(result))

            if args.output:
                # Create temporary scanner for export
                temp_scanner = ModelDrivenSecurityScanner()
                temp_scanner.export_results_json(result, args.output)
        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
