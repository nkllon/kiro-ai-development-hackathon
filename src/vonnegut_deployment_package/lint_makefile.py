#!/usr/bin/env python3
"""
Makefile Linter
===============

Comprehensive linting system for Makefile quality and style.
Enforces best practices, coding standards, and consistency.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Makefile linting and quality assurance
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class LintSeverity(Enum):
    """Lint issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


class LintCategory(Enum):
    """Lint issue categories."""
    SYNTAX = "syntax"
    STYLE = "style"
    BEST_PRACTICES = "best_practices"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


@dataclass
class LintRule:
    """Represents a linting rule."""
    name: str
    description: str
    category: LintCategory
    severity: LintSeverity
    pattern: Optional[str] = None
    check_function: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class LintIssue:
    """Represents a linting issue."""
    rule: str
    severity: LintSeverity
    category: LintCategory
    message: str
    file_path: str
    line_number: int
    column: int = 0
    line_content: str = ""
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class LintReport:
    """Linting report for a file."""
    file_path: str
    total_lines: int
    issues: List[LintIssue] = field(default_factory=list)
    errors: int = 0
    warnings: int = 0
    info: int = 0
    style: int = 0
    score: float = 10.0


class MakefileLinter(ReflectiveModule):
    """
    📋 MAKEFILE LINTER 📋
    
    Comprehensive linting system for Makefile quality assurance.
    Enforces best practices, style guidelines, and security standards.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "makefile_linter"
        self.repository_root = Path(repository_root)
        
        # Linting rules
        self.rules = self._initialize_lint_rules()
        
        # Configuration
        self.config = {
            "max_line_length": 120,
            "require_phony": True,
            "require_help": True,
            "require_comments": True,
            "enforce_naming": True,
            "check_security": True
        }
    
    def _initialize_lint_rules(self) -> Dict[str, LintRule]:
        """Initialize linting rules."""
        rules = {}
        
        # Syntax rules
        rules["tab_indentation"] = LintRule(
            name="tab_indentation",
            description="Commands must be indented with tabs, not spaces",
            category=LintCategory.SYNTAX,
            severity=LintSeverity.ERROR,
            check_function="check_tab_indentation",
            fix_suggestion="Replace leading spaces with tabs in command lines"
        )
        
        rules["line_length"] = LintRule(
            name="line_length",
            description="Lines should not exceed maximum length",
            category=LintCategory.STYLE,
            severity=LintSeverity.WARNING,
            check_function="check_line_length",
            fix_suggestion="Break long lines using backslash continuation"
        )
        
        rules["trailing_whitespace"] = LintRule(
            name="trailing_whitespace",
            description="Lines should not have trailing whitespace",
            category=LintCategory.STYLE,
            severity=LintSeverity.STYLE,
            pattern=r"\s+$",
            fix_suggestion="Remove trailing whitespace"
        )
        
        # Best practices rules
        rules["phony_declaration"] = LintRule(
            name="phony_declaration",
            description="Phony targets should be declared with .PHONY",
            category=LintCategory.BEST_PRACTICES,
            severity=LintSeverity.WARNING,
            check_function="check_phony_declaration",
            fix_suggestion="Add .PHONY declaration for non-file targets"
        )
        
        rules["target_naming"] = LintRule(
            name="target_naming",
            description="Target names should follow naming conventions",
            category=LintCategory.STYLE,
            severity=LintSeverity.INFO,
            pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
            fix_suggestion="Use lowercase letters, numbers, hyphens, and underscores"
        )
        
        rules["variable_naming"] = LintRule(
            name="variable_naming",
            description="Variables should use uppercase names",
            category=LintCategory.STYLE,
            severity=LintSeverity.INFO,
            pattern=r"^[A-Z][A-Z0-9_]*$",
            fix_suggestion="Use uppercase letters and underscores for variable names"
        )
        
        rules["help_target"] = LintRule(
            name="help_target",
            description="Makefile should have a help target",
            category=LintCategory.BEST_PRACTICES,
            severity=LintSeverity.INFO,
            check_function="check_help_target",
            fix_suggestion="Add a help target that lists available targets"
        )
        
        rules["target_documentation"] = LintRule(
            name="target_documentation",
            description="Targets should have documentation comments",
            category=LintCategory.MAINTAINABILITY,
            severity=LintSeverity.INFO,
            check_function="check_target_documentation",
            fix_suggestion="Add ## comments to document target purpose"
        )
        
        # Security rules
        rules["dangerous_commands"] = LintRule(
            name="dangerous_commands",
            description="Dangerous commands should be avoided or protected",
            category=LintCategory.SECURITY,
            severity=LintSeverity.ERROR,
            check_function="check_dangerous_commands",
            fix_suggestion="Add safety checks or confirmation prompts"
        )
        
        rules["hardcoded_paths"] = LintRule(
            name="hardcoded_paths",
            description="Avoid hardcoded absolute paths",
            category=LintCategory.MAINTAINABILITY,
            severity=LintSeverity.WARNING,
            pattern=r"/[a-zA-Z0-9_/]+",
            fix_suggestion="Use variables or relative paths instead"
        )
        
        # Performance rules
        rules["unnecessary_commands"] = LintRule(
            name="unnecessary_commands",
            description="Avoid unnecessary command executions",
            category=LintCategory.PERFORMANCE,
            severity=LintSeverity.INFO,
            check_function="check_unnecessary_commands",
            fix_suggestion="Combine commands or use more efficient alternatives"
        )
        
        rules["parallel_safety"] = LintRule(
            name="parallel_safety",
            description="Targets should be safe for parallel execution",
            category=LintCategory.PERFORMANCE,
            severity=LintSeverity.INFO,
            check_function="check_parallel_safety",
            fix_suggestion="Ensure no file conflicts between parallel targets"
        )
        
        return rules
    
    def lint_file(self, file_path: Path) -> LintReport:
        """Lint a single Makefile."""
        self._logger.info(f"📋 Linting file: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        report = LintReport(
            file_path=str(file_path),
            total_lines=len(lines)
        )
        
        # Run all linting rules
        for rule_name, rule in self.rules.items():
            if rule.pattern:
                self._check_pattern_rule(rule, lines, report)
            elif rule.check_function:
                check_method = getattr(self, rule.check_function, None)
                if check_method:
                    check_method(rule, lines, report)
        
        # Calculate scores
        self._calculate_scores(report)
        
        return report
    
    def _check_pattern_rule(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check a pattern-based rule."""
        for line_num, line in enumerate(lines, 1):
            if re.search(rule.pattern, line):
                issue = LintIssue(
                    rule=rule.name,
                    severity=rule.severity,
                    category=rule.category,
                    message=rule.description,
                    file_path=report.file_path,
                    line_number=line_num,
                    line_content=line.rstrip(),
                    suggestion=rule.fix_suggestion
                )
                report.issues.append(issue)
                self._increment_severity_count(report, rule.severity)
    
    def check_tab_indentation(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for proper tab indentation in commands."""
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Check if line looks like a command (starts with whitespace)
            if line.startswith(' ') and not line.startswith('\t'):
                # This is likely a command indented with spaces
                issue = LintIssue(
                    rule=rule.name,
                    severity=rule.severity,
                    category=rule.category,
                    message="Command indented with spaces instead of tabs",
                    file_path=report.file_path,
                    line_number=line_num,
                    line_content=line.rstrip(),
                    suggestion=rule.fix_suggestion,
                    auto_fixable=True
                )
                report.issues.append(issue)
                self._increment_severity_count(report, rule.severity)
    
    def check_line_length(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for lines exceeding maximum length."""
        max_length = self.config["max_line_length"]
        
        for line_num, line in enumerate(lines, 1):
            if len(line.rstrip()) > max_length:
                issue = LintIssue(
                    rule=rule.name,
                    severity=rule.severity,
                    category=rule.category,
                    message=f"Line exceeds {max_length} characters ({len(line.rstrip())})",
                    file_path=report.file_path,
                    line_number=line_num,
                    line_content=line.rstrip()[:50] + "..." if len(line) > 50 else line.rstrip(),
                    suggestion=rule.fix_suggestion
                )
                report.issues.append(issue)
                self._increment_severity_count(report, rule.severity)
    
    def check_phony_declaration(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for proper .PHONY declarations."""
        if not self.config["require_phony"]:
            return
        
        # Find all targets and .PHONY declarations
        targets = set()
        phony_targets = set()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Find .PHONY declarations
            if line.startswith('.PHONY:'):
                phony_list = line[7:].strip().split()
                phony_targets.update(phony_list)
            
            # Find target definitions
            elif ':' in line and not line.startswith('#') and not line.startswith('\t'):
                target_match = re.match(r'^([^:]+):', line)
                if target_match:
                    target_name = target_match.group(1).strip()
                    targets.add((target_name, line_num))
        
        # Check for common targets that should be phony
        common_phony = {"help", "clean", "test", "install", "deploy", "build", "all", "default"}
        
        for target_name, line_num in targets:
            if target_name in common_phony and target_name not in phony_targets:
                issue = LintIssue(
                    rule=rule.name,
                    severity=rule.severity,
                    category=rule.category,
                    message=f"Target '{target_name}' should be declared as .PHONY",
                    file_path=report.file_path,
                    line_number=line_num,
                    suggestion=f"Add '.PHONY: {target_name}' declaration"
                )
                report.issues.append(issue)
                self._increment_severity_count(report, rule.severity)
    
    def check_help_target(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for presence of help target."""
        if not self.config["require_help"]:
            return
        
        has_help = False
        for line in lines:
            if re.match(r'^help\s*:', line.strip()):
                has_help = True
                break
        
        if not has_help:
            issue = LintIssue(
                rule=rule.name,
                severity=rule.severity,
                category=rule.category,
                message="Makefile should have a help target",
                file_path=report.file_path,
                line_number=1,
                suggestion=rule.fix_suggestion
            )
            report.issues.append(issue)
            self._increment_severity_count(report, rule.severity)
    
    def check_target_documentation(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for target documentation."""
        if not self.config["require_comments"]:
            return
        
        documented_targets = 0
        total_targets = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Find target definitions
            if ':' in line and not line.startswith('#') and not line.startswith('\t'):
                target_match = re.match(r'^([^:]+):', line)
                if target_match:
                    total_targets += 1
                    
                    # Check if target has documentation (## comment)
                    if '##' in line:
                        documented_targets += 1
                    else:
                        # Check previous line for comment
                        if line_num > 1:
                            prev_line = lines[line_num - 2].strip()
                            if prev_line.startswith('#'):
                                documented_targets += 1
                            else:
                                issue = LintIssue(
                                    rule=rule.name,
                                    severity=rule.severity,
                                    category=rule.category,
                                    message=f"Target '{target_match.group(1).strip()}' lacks documentation",
                                    file_path=report.file_path,
                                    line_number=line_num,
                                    suggestion="Add ## comment to document target purpose"
                                )
                                report.issues.append(issue)
                                self._increment_severity_count(report, rule.severity)
        
        # Overall documentation score
        if total_targets > 0:
            doc_ratio = documented_targets / total_targets
            if doc_ratio < 0.5:  # Less than 50% documented
                issue = LintIssue(
                    rule=rule.name,
                    severity=LintSeverity.WARNING,
                    category=rule.category,
                    message=f"Low documentation coverage: {doc_ratio:.1%} of targets documented",
                    file_path=report.file_path,
                    line_number=1,
                    suggestion="Add documentation comments for more targets"
                )
                report.issues.append(issue)
                self._increment_severity_count(report, LintSeverity.WARNING)
    
    def check_dangerous_commands(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for dangerous commands."""
        if not self.config["check_security"]:
            return
        
        dangerous_patterns = [
            (r"rm\s+-rf\s+/", "Dangerous: recursive delete from root"),
            (r"rm\s+-rf\s+\*", "Dangerous: recursive delete with wildcard"),
            (r"sudo\s+rm", "Dangerous: sudo delete command"),
            (r"chmod\s+777", "Dangerous: overly permissive file permissions"),
            (r"curl.*\|\s*sh", "Dangerous: piping remote content to shell"),
            (r"wget.*\|\s*sh", "Dangerous: piping remote content to shell")
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, message in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = LintIssue(
                        rule=rule.name,
                        severity=rule.severity,
                        category=rule.category,
                        message=message,
                        file_path=report.file_path,
                        line_number=line_num,
                        line_content=line.rstrip(),
                        suggestion=rule.fix_suggestion
                    )
                    report.issues.append(issue)
                    self._increment_severity_count(report, rule.severity)
    
    def check_unnecessary_commands(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for unnecessary or inefficient commands."""
        inefficient_patterns = [
            (r"cat\s+\S+\s*\|\s*grep", "Use grep directly instead of cat | grep"),
            (r"echo\s+.*\s*>\s*\S+\s*&&\s*cat\s+\S+", "Combine echo and output redirection"),
            (r"mkdir\s+\S+\s*&&\s*cd\s+\S+", "Use mkdir -p and consider directory structure")
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, suggestion in inefficient_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = LintIssue(
                        rule=rule.name,
                        severity=rule.severity,
                        category=rule.category,
                        message="Inefficient command pattern detected",
                        file_path=report.file_path,
                        line_number=line_num,
                        line_content=line.rstrip(),
                        suggestion=suggestion
                    )
                    report.issues.append(issue)
                    self._increment_severity_count(report, rule.severity)
    
    def check_parallel_safety(self, rule: LintRule, lines: List[str], report: LintReport):
        """Check for parallel execution safety."""
        # Look for potential file conflicts
        output_files = set()
        targets_with_outputs = {}
        
        current_target = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Find target definitions
            if ':' in line and not line.startswith('#') and not line.startswith('\t'):
                target_match = re.match(r'^([^:]+):', line)
                if target_match:
                    current_target = target_match.group(1).strip()
                    targets_with_outputs[current_target] = []
            
            # Find output redirections in commands
            elif line.startswith('\t') and current_target:
                output_matches = re.findall(r'>\s*([^\s&|;]+)', line)
                for output_file in output_matches:
                    if output_file not in output_files:
                        output_files.add(output_file)
                        targets_with_outputs[current_target].append(output_file)
                    else:
                        # Potential conflict
                        issue = LintIssue(
                            rule=rule.name,
                            severity=rule.severity,
                            category=rule.category,
                            message=f"Potential parallel conflict: multiple targets write to {output_file}",
                            file_path=report.file_path,
                            line_number=line_num,
                            suggestion="Use unique output files or add dependencies"
                        )
                        report.issues.append(issue)
                        self._increment_severity_count(report, rule.severity)
    
    def _increment_severity_count(self, report: LintReport, severity: LintSeverity):
        """Increment severity count in report."""
        if severity == LintSeverity.ERROR:
            report.errors += 1
        elif severity == LintSeverity.WARNING:
            report.warnings += 1
        elif severity == LintSeverity.INFO:
            report.info += 1
        elif severity == LintSeverity.STYLE:
            report.style += 1
    
    def _calculate_scores(self, report: LintReport):
        """Calculate quality scores for the report."""
        # Start with perfect score
        score = 10.0
        
        # Deduct points based on severity
        score -= report.errors * 2.0      # Errors: -2 points each
        score -= report.warnings * 0.5    # Warnings: -0.5 points each
        score -= report.info * 0.1         # Info: -0.1 points each
        score -= report.style * 0.05       # Style: -0.05 points each
        
        # Ensure score doesn't go below 0
        report.score = max(0.0, score)
    
    def lint_directory(self, directory: Path = None) -> Dict[str, LintReport]:
        """Lint all Makefiles in a directory."""
        if directory is None:
            directory = self.repository_root
        
        makefile_patterns = ["Makefile", "makefile", "*.mk"]
        reports = {}
        
        # Find all Makefiles
        makefiles = []
        for pattern in makefile_patterns:
            makefiles.extend(directory.rglob(pattern))
        
        # Remove duplicates and sort
        makefiles = sorted(list(set(makefiles)))
        
        self._logger.info(f"📋 Linting {len(makefiles)} Makefiles...")
        
        for makefile in makefiles:
            try:
                report = self.lint_file(makefile)
                reports[str(makefile)] = report
            except Exception as e:
                self._logger.error(f"Failed to lint {makefile}: {e}")
        
        return reports
    
    def generate_lint_report(self, reports: Dict[str, LintReport], 
                           output_file: Optional[Path] = None) -> Path:
        """Generate comprehensive lint report."""
        if output_file is None:
            output_file = self.repository_root / "reports" / "makefile_lint_report.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate summary statistics
        total_files = len(reports)
        total_issues = sum(len(report.issues) for report in reports.values())
        total_errors = sum(report.errors for report in reports.values())
        total_warnings = sum(report.warnings for report in reports.values())
        average_score = sum(report.score for report in reports.values()) / total_files if total_files > 0 else 0
        
        report_data = {
            "timestamp": self._get_current_timestamp(),
            "summary": {
                "total_files": total_files,
                "total_issues": total_issues,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "average_score": average_score,
                "files_with_errors": len([r for r in reports.values() if r.errors > 0]),
                "files_with_warnings": len([r for r in reports.values() if r.warnings > 0])
            },
            "files": {
                file_path: {
                    "total_lines": report.total_lines,
                    "score": report.score,
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "info": report.info,
                    "style": report.style,
                    "issues": [
                        {
                            "rule": issue.rule,
                            "severity": issue.severity.value,
                            "category": issue.category.value,
                            "message": issue.message,
                            "line_number": issue.line_number,
                            "line_content": issue.line_content,
                            "suggestion": issue.suggestion,
                            "auto_fixable": issue.auto_fixable
                        }
                        for issue in report.issues
                    ]
                }
                for file_path, report in reports.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self._logger.info(f"📊 Lint report saved: {output_file}")
        return output_file


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Linter")
    parser.add_argument("files", nargs="*", help="Makefile(s) to lint")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--config", help="Configuration file")
    parser.add_argument("--report", help="Generate lint report to file")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--severity", choices=["error", "warning", "info", "style"],
                       default="warning", help="Minimum severity to report")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create linter
    linter = MakefileLinter(args.root)
    
    # Load custom config if provided
    if args.config:
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
            linter.config.update(custom_config)
    
    # Determine files to lint
    if args.files:
        # Lint specific files
        reports = {}
        for file_path in args.files:
            path = Path(file_path)
            if path.exists():
                reports[str(path)] = linter.lint_file(path)
            else:
                print(f"File not found: {file_path}")
    else:
        # Lint all Makefiles in directory
        reports = linter.lint_directory()
    
    # Filter by severity
    min_severity = LintSeverity(args.severity)
    severity_order = [LintSeverity.ERROR, LintSeverity.WARNING, LintSeverity.INFO, LintSeverity.STYLE]
    min_level = severity_order.index(min_severity)
    
    # Display results
    total_issues = 0
    for file_path, report in reports.items():
        filtered_issues = [
            issue for issue in report.issues 
            if severity_order.index(issue.severity) <= min_level
        ]
        
        if filtered_issues or args.verbose:
            print(f"\n📋 {file_path}")
            print(f"Score: {report.score:.1f}/10.0")
            print(f"Issues: {len(filtered_issues)} (E:{report.errors} W:{report.warnings} I:{report.info} S:{report.style})")
            
            for issue in filtered_issues:
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "style": "💅"}[issue.severity.value]
                print(f"  {severity_icon} Line {issue.line_number}: {issue.message}")
                if issue.suggestion and args.verbose:
                    print(f"      💡 {issue.suggestion}")
                if issue.line_content and args.verbose:
                    print(f"      📝 {issue.line_content}")
            
            total_issues += len(filtered_issues)
    
    # Summary
    if reports:
        avg_score = sum(r.score for r in reports.values()) / len(reports)
        print(f"\n📊 SUMMARY")
        print(f"Files: {len(reports)}")
        print(f"Average Score: {avg_score:.1f}/10.0")
        print(f"Total Issues: {total_issues}")
    
    # Generate report if requested
    if args.report:
        report_path = linter.generate_lint_report(reports, Path(args.report))
        print(f"\n📊 Lint report saved: {report_path}")
    
    # Exit with appropriate code
    total_errors = sum(r.errors for r in reports.values())
    if total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()