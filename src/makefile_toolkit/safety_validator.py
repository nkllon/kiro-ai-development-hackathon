#!/usr/bin/env python3
"""
Makefile Safety Validator
=========================

Comprehensive safety validation system for Makefile operations.
Provides prerequisite checking, confirmation prompts, and error handling.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Safety validation and error handling for Makefile operations
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleCapability,
    ModuleHealth,
    ModuleStatus,
    GracefulDegradationResult,
)


class SafetyLevel(Enum):
    """Safety levels for operations."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    DESTRUCTIVE = "destructive"


class ValidationResult(Enum):
    """Validation result types."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    BLOCK = "block"


@dataclass
class SafetyCheck:
    """Represents a safety check."""
    name: str
    description: str
    check_function: str
    safety_level: SafetyLevel
    required: bool = True
    error_message: str = ""
    suggestion: str = ""


@dataclass
class ValidationReport:
    """Safety validation report."""
    target: str
    overall_result: ValidationResult
    safety_level: SafetyLevel
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    messages: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    can_proceed: bool = False


class MakefileSafetyValidator(ReflectiveModule):
    """
    🛡️ MAKEFILE SAFETY VALIDATOR 🛡️
    
    Comprehensive safety validation system for Makefile operations.
    Prevents dangerous operations and provides clear guidance.
    """
    
    def __init__(self, repository_root: str = "."):
        self.module_id = "makefile_safety_validator"
        self.repository_root = Path(repository_root)
        
        # Safety checks registry
        self.safety_checks = self._initialize_safety_checks()
        
        # Dangerous operations patterns
        self.dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Root deletion
            r"rm\s+-rf\s+\*",  # Wildcard deletion
            r"sudo\s+rm",  # Sudo deletion
            r"format\s+[A-Z]:",  # Drive formatting
            r"dd\s+if=.*of=/dev/",  # Disk writing
            r"chmod\s+777",  # Dangerous permissions
            r"chown\s+.*:.*\s+/",  # Root ownership changes
        ]
        
        # Protected paths
        self.protected_paths = [
            "/",
            "/usr",
            "/bin",
            "/sbin",
            "/etc",
            "/var",
            "/home",
            "/root",
            "C:\\",
            "C:\\Windows",
            "C:\\Program Files"
        ]
        
        # Required tools
        self.required_tools = {
            "git": {
                "description": "Git version control",
                "commands": ["git"],
            },
            "python": {
                "description": "Python interpreter",
                "commands": ["python", "python3"],
            },
            "make": {
                "description": "Make build tool",
                "commands": ["make"],
            },
        }

        super().__init__()

        super().__init__()

    def get_module_info(self) -> Dict[str, Any]:
        """Metadata for reflective module interfaces."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Safety Validator",
            "version": "1.0.0",
            "repository_root": str(self.repository_root.resolve()),
            "registered_checks": len(self.safety_checks),
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Module capability declaration."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
        ]

    def get_health_status(self) -> ModuleHealth:
        """Report validator health metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        issues: List[str] = []
        missing_tools = [
            tool
            for tool, meta in self.required_tools.items()
            if not any(shutil.which(cmd) for cmd in meta["commands"])
        ]
        if missing_tools:
            issues.append(f"Missing required tools: {', '.join(missing_tools)}")

        status = ModuleStatus.HEALTHY if not missing_tools else ModuleStatus.WARNING
        health_score = 1.0 if status == ModuleStatus.HEALTHY else 0.7

        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count,
        )

    def graceful_degradation(self) -> GracefulDegradationResult:
        """Fallback behaviour when dependencies are missing."""
        remaining = [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.VALIDATION]
        degraded = [ModuleCapability.MONITORING]
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded,
            remaining_capabilities=remaining,
            error_message=None,
        )
    
    def _initialize_safety_checks(self) -> Dict[str, SafetyCheck]:
        """Initialize safety checks registry."""
        return {
            "git_status": SafetyCheck(
                name="Git Status Check",
                description="Verify git repository is in clean state",
                check_function="check_git_status",
                safety_level=SafetyLevel.CAUTION,
                error_message="Git repository has uncommitted changes",
                suggestion="Commit or stash changes before proceeding"
            ),
            "disk_space": SafetyCheck(
                name="Disk Space Check",
                description="Verify sufficient disk space available",
                check_function="check_disk_space",
                safety_level=SafetyLevel.SAFE,
                error_message="Insufficient disk space",
                suggestion="Free up disk space before proceeding"
            ),
            "process_conflicts": SafetyCheck(
                name="Process Conflict Check",
                description="Check for conflicting processes",
                check_function="check_process_conflicts",
                safety_level=SafetyLevel.CAUTION,
                error_message="Conflicting processes detected",
                suggestion="Stop conflicting processes before proceeding"
            ),
            "file_permissions": SafetyCheck(
                name="File Permissions Check",
                description="Verify required file permissions",
                check_function="check_file_permissions",
                safety_level=SafetyLevel.SAFE,
                error_message="Insufficient file permissions",
                suggestion="Check file permissions and ownership"
            ),
            "network_connectivity": SafetyCheck(
                name="Network Connectivity Check",
                description="Verify network connectivity for remote operations",
                check_function="check_network_connectivity",
                safety_level=SafetyLevel.SAFE,
                required=False,
                error_message="Network connectivity issues",
                suggestion="Check network connection and try again"
            ),
            "tool_availability": SafetyCheck(
                name="Tool Availability Check",
                description="Verify required tools are available",
                check_function="check_tool_availability",
                safety_level=SafetyLevel.SAFE,
                error_message="Required tools not available",
                suggestion="Install missing tools before proceeding"
            ),
            "dangerous_operations": SafetyCheck(
                name="Dangerous Operations Check",
                description="Scan for dangerous operation patterns",
                check_function="check_dangerous_operations",
                safety_level=SafetyLevel.DESTRUCTIVE,
                error_message="Dangerous operations detected",
                suggestion="Review and confirm dangerous operations"
            ),
            "protected_paths": SafetyCheck(
                name="Protected Paths Check",
                description="Verify operations don't affect protected paths",
                check_function="check_protected_paths",
                safety_level=SafetyLevel.DESTRUCTIVE,
                error_message="Operations affect protected system paths",
                suggestion="Avoid operations on protected system paths"
            )
        }
    
    def validate_target(self, target: str, target_commands: List[str] = None) -> ValidationReport:
        """Validate a Makefile target for safety."""
        self._logger.info(f"🛡️ Validating target: {target}")
        
        report = ValidationReport(
            target=target,
            overall_result=ValidationResult.PASS,
            safety_level=SafetyLevel.SAFE
        )
        
        # Determine target safety level
        target_safety_level = self._assess_target_safety_level(target, target_commands)
        report.safety_level = target_safety_level
        
        # Run applicable safety checks
        applicable_checks = self._get_applicable_checks(target, target_safety_level)
        
        for check_name in applicable_checks:
            check = self.safety_checks[check_name]
            result = self._run_safety_check(check, target, target_commands)
            
            if result == ValidationResult.PASS:
                report.checks_passed += 1
            elif result == ValidationResult.WARN:
                report.checks_warned += 1
                report.messages.append(f"⚠️ {check.description}: {check.error_message}")
                if check.suggestion:
                    report.suggestions.append(check.suggestion)
            elif result == ValidationResult.FAIL:
                report.checks_failed += 1
                report.messages.append(f"❌ {check.description}: {check.error_message}")
                if check.suggestion:
                    report.suggestions.append(check.suggestion)
                if check.required:
                    report.overall_result = ValidationResult.FAIL
            elif result == ValidationResult.BLOCK:
                report.checks_failed += 1
                report.messages.append(f"🚫 {check.description}: {check.error_message}")
                if check.suggestion:
                    report.suggestions.append(check.suggestion)
                report.overall_result = ValidationResult.BLOCK
        
        # Determine if can proceed
        report.can_proceed = report.overall_result in [ValidationResult.PASS, ValidationResult.WARN]
        
        self._logger.info(f"✅ Validation complete: {report.overall_result.value}")
        return report
    
    def _assess_target_safety_level(self, target: str, commands: List[str] = None) -> SafetyLevel:
        """Assess the safety level of a target."""
        target_lower = target.lower()
        
        # Destructive operations
        destructive_keywords = ["delete", "remove", "purge", "destroy", "wipe", "format", "reset"]
        if any(keyword in target_lower for keyword in destructive_keywords):
            return SafetyLevel.DESTRUCTIVE
        
        # Dangerous operations
        dangerous_keywords = ["deploy", "install", "configure", "modify", "change"]
        if any(keyword in target_lower for keyword in dangerous_keywords):
            return SafetyLevel.DANGEROUS
        
        # Caution operations
        caution_keywords = ["start", "stop", "restart", "build", "compile"]
        if any(keyword in target_lower for keyword in caution_keywords):
            return SafetyLevel.CAUTION
        
        # Check commands if provided
        if commands:
            command_text = " ".join(commands).lower()
            
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                import re
                if re.search(pattern, command_text, re.IGNORECASE):
                    return SafetyLevel.DESTRUCTIVE
            
            # Check for protected paths
            for path in self.protected_paths:
                if path.lower() in command_text:
                    return SafetyLevel.DESTRUCTIVE
        
        return SafetyLevel.SAFE
    
    def _get_applicable_checks(self, target: str, safety_level: SafetyLevel) -> List[str]:
        """Get applicable safety checks for target and safety level."""
        applicable = []
        
        # Always run basic checks
        applicable.extend(["tool_availability", "file_permissions", "disk_space"])
        
        # Add checks based on safety level
        if safety_level in [SafetyLevel.CAUTION, SafetyLevel.DANGEROUS, SafetyLevel.DESTRUCTIVE]:
            applicable.extend(["git_status", "process_conflicts"])
        
        if safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.DESTRUCTIVE]:
            applicable.extend(["dangerous_operations", "protected_paths"])
        
        # Add network check for deployment targets
        if "deploy" in target.lower() or "install" in target.lower():
            applicable.append("network_connectivity")
        
        return applicable
    
    def _run_safety_check(self, check: SafetyCheck, target: str, commands: List[str] = None) -> ValidationResult:
        """Run a specific safety check."""
        try:
            check_method = getattr(self, check.check_function)
            return check_method(target, commands)
        except AttributeError:
            self._logger.warning(f"Safety check method not found: {check.check_function}")
            return ValidationResult.WARN
        except Exception as e:
            self._logger.error(f"Safety check failed: {check.check_function}: {e}")
            return ValidationResult.WARN
    
    def check_git_status(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repository_root,
                timeout=10
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    return ValidationResult.WARN  # Uncommitted changes
                return ValidationResult.PASS
            else:
                return ValidationResult.WARN  # Not a git repo or other issue
                
        except Exception:
            return ValidationResult.WARN
    
    def check_disk_space(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.repository_root)
            
            # Require at least 1GB free space
            min_free_bytes = 1024 * 1024 * 1024  # 1GB
            
            if free < min_free_bytes:
                return ValidationResult.FAIL
            elif free < min_free_bytes * 2:  # Less than 2GB
                return ValidationResult.WARN
            else:
                return ValidationResult.PASS
                
        except Exception:
            return ValidationResult.WARN
    
    def check_process_conflicts(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check for conflicting processes."""
        try:
            # Check for common conflicting processes
            conflicting_processes = ["make", "python", "node", "npm", "docker"]
            
            if sys.platform == "win32":
                # Windows process check
                result = subprocess.run(
                    ["tasklist", "/FO", "CSV"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    running_processes = result.stdout.lower()
                    conflicts = [proc for proc in conflicting_processes if proc in running_processes]
                    
                    if conflicts:
                        return ValidationResult.WARN
            else:
                # Unix process check
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    running_processes = result.stdout.lower()
                    conflicts = [proc for proc in conflicting_processes if proc in running_processes]
                    
                    if conflicts:
                        return ValidationResult.WARN
            
            return ValidationResult.PASS
            
        except Exception:
            return ValidationResult.WARN
    
    def check_file_permissions(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check file permissions."""
        try:
            # Check if we can write to repository root
            test_file = self.repository_root / ".permission_test"
            
            try:
                test_file.write_text("test")
                test_file.unlink()
                return ValidationResult.PASS
            except PermissionError:
                return ValidationResult.FAIL
            except Exception:
                return ValidationResult.WARN
                
        except Exception:
            return ValidationResult.WARN
    
    def check_network_connectivity(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check network connectivity."""
        try:
            import socket
            
            # Test connectivity to common services
            test_hosts = [
                ("8.8.8.8", 53),  # Google DNS
                ("github.com", 443),  # GitHub
            ]
            
            for host, port in test_hosts:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(5)
                        result = sock.connect_ex((host, port))
                        if result == 0:
                            return ValidationResult.PASS
                except Exception:
                    continue
            
            return ValidationResult.WARN
            
        except Exception:
            return ValidationResult.WARN
    
    def check_tool_availability(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check required tool availability."""
        missing_tools = []
        
        for tool, meta in self.required_tools.items():
            if not any(self._is_tool_available(cmd) for cmd in meta["commands"]):
                missing_tools.append(f"{tool} ({meta['description']})")
        
        if missing_tools:
            return ValidationResult.FAIL
        
        return ValidationResult.PASS
    
    def _is_tool_available(self, tool: str) -> bool:
        """Check if a tool is available."""
        try:
            subprocess.run(
                [tool, "--version"],
                capture_output=True,
                timeout=5
            )
            return True
        except Exception:
            return False
    
    def check_dangerous_operations(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check for dangerous operation patterns."""
        if not commands:
            return ValidationResult.PASS
        
        command_text = " ".join(commands)
        
        import re
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command_text, re.IGNORECASE):
                return ValidationResult.BLOCK
        
        return ValidationResult.PASS
    
    def check_protected_paths(self, target: str, commands: List[str] = None) -> ValidationResult:
        """Check for operations on protected paths."""
        if not commands:
            return ValidationResult.PASS
        
        command_text = " ".join(commands).lower()
        
        for path in self.protected_paths:
            if path.lower() in command_text:
                return ValidationResult.BLOCK
        
        return ValidationResult.PASS
    
    def prompt_user_confirmation(self, report: ValidationReport) -> bool:
        """Prompt user for confirmation based on validation report."""
        if report.safety_level == SafetyLevel.SAFE and report.overall_result == ValidationResult.PASS:
            return True
        
        print(f"\n🛡️ SAFETY VALIDATION REPORT for target '{report.target}'")
        print(f"Safety Level: {report.safety_level.value.upper()}")
        print(f"Overall Result: {report.overall_result.value.upper()}")
        print(f"Checks: {report.checks_passed} passed, {report.checks_warned} warned, {report.checks_failed} failed")
        
        if report.messages:
            print("\nIssues found:")
            for message in report.messages:
                print(f"  {message}")
        
        if report.suggestions:
            print("\nSuggestions:")
            for suggestion in report.suggestions:
                print(f"  💡 {suggestion}")
        
        if not report.can_proceed:
            print("\n🚫 Cannot proceed due to safety violations.")
            return False
        
        if report.safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.DESTRUCTIVE]:
            print(f"\n⚠️ This is a {report.safety_level.value.upper()} operation!")
            response = input("Do you want to proceed? (yes/no): ").lower().strip()
            return response in ["yes", "y"]
        
        if report.overall_result == ValidationResult.WARN:
            response = input("\nProceed despite warnings? (yes/no): ").lower().strip()
            return response in ["yes", "y"]
        
        return True
    
    def generate_safety_report(self, reports: List[ValidationReport]) -> Dict[str, Any]:
        """Generate comprehensive safety report."""
        total_targets = len(reports)
        safe_targets = len([r for r in reports if r.safety_level == SafetyLevel.SAFE])
        dangerous_targets = len([r for r in reports if r.safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.DESTRUCTIVE]])
        
        return {
            "timestamp": self._get_current_timestamp(),
            "summary": {
                "total_targets": total_targets,
                "safe_targets": safe_targets,
                "dangerous_targets": dangerous_targets,
                "overall_safety_score": safe_targets / total_targets if total_targets > 0 else 0
            },
            "reports": [
                {
                    "target": report.target,
                    "safety_level": report.safety_level.value,
                    "result": report.overall_result.value,
                    "can_proceed": report.can_proceed,
                    "checks_passed": report.checks_passed,
                    "checks_failed": report.checks_failed,
                    "messages": report.messages,
                    "suggestions": report.suggestions
                }
                for report in reports
            ]
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Safety Validator")
    parser.add_argument("target", help="Target to validate")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--commands", nargs="*", help="Target commands to validate")
    parser.add_argument("--interactive", action="store_true", help="Interactive confirmation prompts")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run validation
    validator = MakefileSafetyValidator(args.root)
    report = validator.validate_target(args.target, args.commands)
    
    # Print report
    print(f"\n🛡️ SAFETY VALIDATION COMPLETE")
    print(f"Target: {report.target}")
    print(f"Safety Level: {report.safety_level.value.upper()}")
    print(f"Result: {report.overall_result.value.upper()}")
    print(f"Can Proceed: {'✅ YES' if report.can_proceed else '❌ NO'}")
    
    if report.messages:
        print("\nMessages:")
        for message in report.messages:
            print(f"  {message}")
    
    if report.suggestions:
        print("\nSuggestions:")
        for suggestion in report.suggestions:
            print(f"  💡 {suggestion}")
    
    # Interactive confirmation if requested
    if args.interactive:
        can_proceed = validator.prompt_user_confirmation(report)
        sys.exit(0 if can_proceed else 1)
    else:
        sys.exit(0 if report.can_proceed else 1)


if __name__ == "__main__":
    main()
