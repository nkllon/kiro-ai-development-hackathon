#!/usr/bin/env python3
"""
One-Liner Linter and Code Quality Tool

This tool detects, analyzes, and fixes one-liner issues and other linting problems
in the codebase. It provides comprehensive analysis and automated fixes where possible.

Usage:
    python scripts/one_liner_linter.py --scan .                    # Scan entire codebase
    python scripts/one_liner_linter.py --fix .                     # Fix issues automatically
    python scripts/one_liner_linter.py --report .                  # Generate detailed report
    python scripts/one_liner_linter.py --check-file path/to/file   # Check specific file
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LintingIssue:
    """Represents a linting issue found in the codebase"""

    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str
    auto_fixable: bool
    context: str


@dataclass
class FileAnalysis:
    """Represents analysis results for a single file"""

    file_path: str
    file_type: str
    total_issues: int
    critical_issues: int
    warnings: int
    suggestions: int
    issues: list[LintingIssue]
    one_liner_score: float  # 0.0 = perfect, 1.0 = all one-liners


class OneLinerLinter:
    """Comprehensive linter for detecting and fixing one-liner issues"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.issues: list[LintingIssue] = []
        self.file_analyses: dict[str, FileAnalysis] = {}

        # Define issue patterns
        self.one_liner_patterns = {
            "bash_oneliner": r'^[^#]*\b(bash|sh|zsh)\s+-c\s+["\'`].*[`"\']\s*$',
            "git_oneliner": r'^[^#]*\bgit\s+( \
    commit|push|pull|checkout|branch)\s+-m\s+["\'`].*[`"\']\s*$',
            "python_oneliner": r'^[^#]*\bpython\s+-c\s+["\'`].*[`"\']\s*$',
            "docker_oneliner": r'^[^#]*\bdocker\s+run\s+.*["\'`].*[`"\']\s*$',
            "kubectl_oneliner": r'^[^#]*\bkubectl\s+.*["\'`].*[`"\']\s*$',
            "gcloud_oneliner": r'^[^#]*\bgcloud\s+.*["\'`].*[`"\']\s*$',
        }

        # Define file extensions to analyze
        self.analyzed_extensions = {
            ".py",
            ".sh",
            ".bash",
            ".zsh",
            ".yaml",
            ".yml",
            ".json",
            ".md",
            ".txt",
            ".cfg",
            ".conf",
            ".ini",
            ".toml",
        }

        # Define directories to exclude
        self.excluded_dirs = {
            ".git",
            ".mypy_cache",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
        }

    def scan_codebase(self, target_path: str = None) -> dict[str, Any]:
        """Scan the entire codebase for linting issues"""
        target = Path(target_path) if target_path else self.workspace_path

        print(f"🔍 Scanning codebase: {target}")
        print(f"📁 Workspace: {self.workspace_path}")

        # Scan all files
        for file_path in self._get_files_to_analyze(target):
            self._analyze_file(file_path)

        # Generate summary
        summary = self._generate_summary()

        print(f"\n📊 Scan Complete!")
        print(f"   Files analyzed: {len(self.file_analyses)}")
        print(f"   Total issues: {len(self.issues)}")
        print(f"   Critical issues: {summary['critical_count']}")
        print(f"   Warnings: {summary['warning_count']}")
        print(f"   Suggestions: {summary['suggestion_count']}")

        return summary

    def _get_files_to_analyze(self, target_path: Path) -> list[Path]:
        """Get list of files to analyze, respecting exclusions"""
        files = []

        for root, dirs, filenames in os.walk(target_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for filename in filenames:
                file_path = Path(root) / filename

                # Check if file should be analyzed
                if file_path.suffix in self.analyzed_extensions or file_path.name in [
                    ".gitignore",
                    "Makefile",
                    "Dockerfile",
                ]:
                    files.append(file_path)

        return files

    def _analyze_file(self, file_path: Path):
        """Analyze a single file for linting issues"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return

        file_issues = []
        file_type = self._detect_file_type(file_path)

        # Analyze based on file type
        if file_type == "python":
            file_issues.extend(self._analyze_python_file(file_path, content, lines))
        elif file_type == "shell":
            file_issues.extend(self._analyze_shell_file(file_path, content, lines))
        elif file_type == "yaml":
            file_issues.extend(self._analyze_yaml_file(file_path, content, lines))
        elif file_type == "markdown":
            file_issues.extend(self._analyze_markdown_file(file_path, content, lines))
        else:
            file_issues.extend(self._analyze_generic_file(file_path, content, lines))

        # Calculate one-liner score
        one_liner_score = self._calculate_one_liner_score(lines)

        # Create file analysis
        analysis = FileAnalysis(
            file_path=str(file_path),
            file_type=file_type,
            total_issues=len(file_issues),
            critical_issues=len([i for i in file_issues if i.severity == "critical"]),
            warnings=len([i for i in file_issues if i.severity == "warning"]),
            suggestions=len([i for i in file_issues if i.severity == "suggestion"]),
            issues=file_issues,
            one_liner_score=one_liner_score,
        )

        self.file_analyses[str(file_path)] = analysis
        self.issues.extend(file_issues)

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect the type of file based on extension and content"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()

        if ext == ".py":
            return "python"
        if ext in [".sh", ".bash", ".zsh"] or name in ["Makefile", "Dockerfile"]:
            return "shell"
        if ext in [".yaml", ".yml"]:
            return "yaml"
        if ext == ".md":
            return "markdown"
        if ext == ".json":
            return "json"
        return "generic"

    def _analyze_python_file(self, file_path: Path, content: str, lines: list[str]) -> list[LintingIssue]:
        """Analyze Python file for linting issues"""
        issues = []

        try:
            # Parse AST to check for syntax errors
            ast.parse(content)
        except SyntaxError as e:
            issues.append(
                LintingIssue(
                    file_path=str(file_path),
                    line_number=e.lineno,
                    issue_type="syntax_error",
                    severity="critical",
                    description=f"Syntax error: {e.msg}",
                    suggestion="Fix the syntax error in the code",
                    auto_fixable=False,
                    context=(lines[e.lineno - 1] if e.lineno <= len(lines) else "Unknown"),
                )
            )

        # Check for one-liner patterns
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for one-liner imports
            if re.match(r"^import\s+.*,.*$", line):
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="one_line_import",
                        severity="warning",
                        description="Multiple imports on one line",
                        suggestion="Split imports onto separate lines for readability",
                        auto_fixable=True,
                        context=line,
                    )
                )

            # Check for long lines
            if len(line) > 88:  # Black's default line length
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="line_too_long",
                        severity="warning",
                        description=f"Line is {len(line)} characters long (max 88)",
                        suggestion="Break long line into multiple lines",
                        auto_fixable=True,
                        context=line,
                    )
                )

            # Check for missing blank lines
            if i > 1 and not lines[i - 2].strip() and not lines[i - 1].strip():
                if re.match(r"^(class|def)\s+", line):
                    issues.append(
                        LintingIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="missing_blank_lines",
                            severity="warning",
                            description="Missing blank lines before class/function definition",
                            suggestion="Add two blank lines before class/function definitions",
                            auto_fixable=True,
                            context=line,
                        )
                    )

        return issues

    def _analyze_shell_file(self, file_path: Path, content: str, lines: list[str]) -> list[LintingIssue]:
        """Analyze shell file for linting issues"""
        issues = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for one-liner patterns
            for pattern_name, pattern in self.one_liner_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        LintingIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="one_liner_detected",
                            severity="critical",
                            description=f"One-liner detected: {pattern_name}",
                            suggestion="Break complex commands into multiple lines or create a proper script",
                            auto_fixable=False,
                            context=line,
                        )
                    )

            # Check for long lines
            if len(line) > 120:
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="line_too_long",
                        severity="warning",
                        description=f"Line is {len(line)} characters long (max 120)",
                        suggestion="Break long command into multiple lines using \\",
                        auto_fixable=True,
                        context=line,
                    )
                )

            # Check for unquoted variables
            if re.search(r'\$[A-Za-z_][A-Za-z0-9_]*[^"\s]', line):
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="unquoted_variable",
                        severity="warning",
                        description="Variable should be quoted to handle spaces and special characters",
                        suggestion='Quote variables: "$VARIABLE" instead of $VARIABLE',
                        auto_fixable=True,
                        context=line,
                    )
                )

        return issues

    def _analyze_yaml_file(self, file_path: Path, content: str, lines: list[str]) -> list[LintingIssue]:
        """Analyze YAML file for linting issues"""
        issues = []

        # Check for hardcoded credentials
        credential_patterns = [
            r'api_key:\s*["\'`][^"\']*["\'`]',
            r'password:\s*["\'`][^"\']*["\'`]',
            r'secret:\s*["\'`][^"\']*["\'`]',
            r'token:\s*["\'`][^"\']*["\'`]',
            r'key:\s*["\'`][^"\']*["\'`]',
        ]

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for hardcoded credentials
            for pattern in credential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        LintingIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="hardcoded_credential",
                            severity="critical",
                            description="Hardcoded credential detected",
                            suggestion="Use environment variables or secret management instead of hardcoded values",
                            auto_fixable=False,
                            context=line,
                        )
                    )

            # Check for long lines
            if len(line) > 120:
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="line_too_long",
                        severity="warning",
                        description=f"Line is {len(line)} characters long (max 120)",
                        suggestion="Break long line or restructure YAML",
                        auto_fixable=True,
                        context=line,
                    )
                )

        return issues

    def _analyze_markdown_file(self, file_path: Path, content: str, lines: list[str]) -> list[LintingIssue]:
        """Analyze Markdown file for linting issues"""
        issues = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for one-liner commit messages
            if re.match(r'^[^#]*\b(git|commit|push|pull)\b.*["\'`].*[`"\']\s*$', line):
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="one_line_commit",
                        severity="warning",
                        description="One-line commit message detected",
                        suggestion="Use multi-line commit messages with proper descriptions",
                        auto_fixable=False,
                        context=line,
                    )
                )

            # Check for long lines
            if len(line) > 100:
                issues.append(
                    LintingIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="line_too_long",
                        severity="suggestion",
                        description=f"Line is {len(line)} characters long (max 100)",
                        suggestion="Break long line for better readability",
                        auto_fixable=True,
                        context=line,
                    )
                )

        return issues

    def _analyze_generic_file(self, file_path: Path, content: str, lines: list[str]) -> list[LintingIssue]:
        """Analyze generic file for basic linting issues"""
        issues = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for one-liner patterns
            for pattern_name, pattern in self.one_liner_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        LintingIssue(
                            file_path=str(file_path),
                            line_number=i,
                            issue_type="one_liner_detected",
                            severity="warning",
                            description=f"One-liner detected: {pattern_name}",
                            suggestion="Consider breaking into multiple lines for readability",
                            auto_fixable=False,
                            context=line,
                        )
                    )

        return issues

    def _calculate_one_liner_score(self, lines: list[str]) -> float:
        """Calculate a score indicating how much the file uses one-liners (0.0  = \
     perfect, 1.0 = all one-liners)"""
        if not lines:
            return 0.0

        one_liner_count = 0
        total_lines = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            total_lines += 1

            # Check if line is a one-liner
            for pattern in self.one_liner_patterns.values():
                if re.search(pattern, line, re.IGNORECASE):
                    one_liner_count += 1
                    break

        if total_lines == 0:
            return 0.0

        return one_liner_count / total_lines

    def _generate_summary(self) -> dict[str, Any]:
        """Generate a summary of all linting issues"""
        critical_count = len([i for i in self.issues if i.severity == "critical"])
        warning_count = len([i for i in self.issues if i.severity == "warning"])
        suggestion_count = len([i for i in self.issues if i.severity == "suggestion"])

        # Group issues by type (count only, not the full objects)
        issues_by_type = {}
        for issue in self.issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = 0
            issues_by_type[issue.issue_type] += 1

        # Calculate average one-liner score
        total_score = sum(analysis.one_liner_score for analysis in self.file_analyses.values())
        avg_one_liner_score = total_score / len(self.file_analyses) if self.file_analyses else 0.0

        return {
            "total_files": len(self.file_analyses),
            "total_issues": len(self.issues),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "suggestion_count": suggestion_count,
            "issues_by_type": issues_by_type,
            "avg_one_liner_score": avg_one_liner_score,
            "files_with_issues": len([f for f in self.file_analyses.values() if f.total_issues > 0]),
        }

    def generate_report(self, output_file: str = None) -> str:
        """Generate a detailed report of all linting issues"""
        summary = self._generate_summary()

        report_lines = [
            "# 🔍 One-Liner Linter Report",
            f"Generated: {datetime.now().isoformat()}",
            f"Workspace: {self.workspace_path}",
            "",
            "## 📊 Summary",
            f"- Files analyzed: {summary['total_files']}",
            f"- Total issues: {summary['total_issues']}",
            f"- Critical issues: {summary['critical_count']}",
            f"- Warnings: {summary['warning_count']}",
            f"- Suggestions: {summary['suggestion_count']}",
            f"- Files with issues: {summary['files_with_issues']}",
            f"- Average one-liner score: {summary['avg_one_liner_score']:.2%}",
            "",
            "## 🚨 Critical Issues",
        ]

        critical_issues = [i for i in self.issues if i.severity == "critical"]
        if critical_issues:
            for issue in critical_issues:
                report_lines.extend(
                    [
                        f"### {issue.file_path}:{issue.line_number}",
                        f"**Type:** {issue.issue_type}",
                        f"**Description:** {issue.description}",
                        f"**Suggestion:** {issue.suggestion}",
                        f"**Context:** `{issue.context}`",
                        "",
                    ]
                )
        else:
            report_lines.append("No critical issues found! 🎉")

        report_lines.extend(
            [
                "## ⚠️  Warnings",
            ]
        )

        warning_issues = [i for i in self.issues if i.severity == "warning"]
        if warning_issues:
            for issue in warning_issues:
                report_lines.extend(
                    [
                        f"### {issue.file_path}:{issue.line_number}",
                        f"**Type:** {issue.issue_type}",
                        f"**Description:** {issue.description}",
                        f"**Suggestion:** {issue.suggestion}",
                        f"**Context:** `{issue.context}`",
                        "",
                    ]
                )
        else:
            report_lines.append("No warnings found! 🎉")

        report_lines.extend(
            [
                "## 💡 Suggestions",
            ]
        )

        suggestion_issues = [i for i in self.issues if i.severity == "suggestion"]
        if suggestion_issues:
            for issue in suggestion_issues:
                report_lines.extend(
                    [
                        f"### {issue.file_path}:{issue.line_number}",
                        f"**Type:** {issue.issue_type}",
                        f"**Description:** {issue.description}",
                        f"**Suggestion:** {issue.suggestion}",
                        f"**Context:** `{issue.context}`",
                        "",
                    ]
                )
        else:
            report_lines.append("No suggestions! 🎉")

        # Add file-by-file breakdown
        report_lines.extend(
            [
                "## 📁 File-by-File Analysis",
            ]
        )

        for file_path, analysis in sorted(self.file_analyses.items()):
            if analysis.total_issues > 0:
                report_lines.extend(
                    [
                        f"### {file_path}",
                        f"- **Type:** {analysis.file_type}",
                        f"- **Issues:** {analysis.total_issues} ( \
    Critical: {analysis.critical_issues}, Warnings: {analysis.warnings}, Suggestions: {analysis.suggestions})",
                        f"- **One-liner Score:** {analysis.one_liner_score:.2%}",
                        "",
                    ]
                )

        report = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")

        return report

    def auto_fix_issues(self) -> dict[str, int]:
        """Automatically fix issues that can be fixed"""
        fixed_counts = {"total_fixed": 0, "files_modified": 0, "errors": 0}

        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.auto_fixable:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)

        for file_path, file_issues in issues_by_file.items():
            try:
                if self._fix_file_issues(file_path, file_issues):
                    fixed_counts["files_modified"] += 1
                    fixed_counts["total_fixed"] += len(file_issues)
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
                fixed_counts["errors"] += 1

        print(f"🔧 Auto-fix complete!")
        print(f"   Files modified: {fixed_counts['files_modified']}")
        print(f"   Issues fixed: {fixed_counts['total_fixed']}")
        print(f"   Errors: {fixed_counts['errors']}")

        return fixed_counts

    def _fix_file_issues(self, file_path: str, issues: list[LintingIssue]) -> bool:
        """Fix issues in a specific file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return False

        # Get file type for this file
        file_type = self._detect_file_type(Path(file_path))

        modified = False
        lines_to_fix = sorted(issues, key=lambda x: x.line_number, reverse=True)

        for issue in lines_to_fix:
            line_idx = issue.line_number - 1

            if line_idx >= len(lines):
                continue

            if issue.issue_type == "line_too_long":
                if self._fix_long_line(lines, line_idx, file_type):
                    modified = True
            elif issue.issue_type == "missing_blank_lines":
                if self._fix_missing_blank_lines(lines, line_idx):
                    modified = True
            elif issue.issue_type == "one_line_import":
                if self._fix_one_line_import(lines, line_idx):
                    modified = True
            elif issue.issue_type == "unquoted_variable":
                if self._fix_unquoted_variable(lines, line_idx):
                    modified = True

        if modified:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                print(f"✅ Fixed issues in {file_path}")
                return True
            except Exception as e:
                print(f"❌ Could not write {file_path}: {e}")
                return False

        return False

    def _fix_long_line(self, lines: list[str], line_idx: int, file_type: str) -> bool:
        """Fix a line that's too long"""
        line = lines[line_idx]

        if file_type == "python":
            # For Python, try to break at logical points
            if "=" in line and len(line) > 88:
                # Break assignment statements
                parts = line.split("=", 1)
                if len(parts) == 2:
                    lines[line_idx] = parts[0] + " = \\"
                    lines.insert(line_idx + 1, "    " + parts[1])
                    return True
            elif "(" in line and ")" in line and len(line) > 88:
                # Break function calls
                if line.count("(") == line.count(")"):
                    # Simple case: single function call
                    open_paren = line.find("(")
                    lines[line_idx] = line[: open_paren + 1] + " \\"
                    lines.insert(line_idx + 1, "    " + line[open_paren + 1 :])
                    return True

        elif file_type == "shell":
            # For shell, break at logical points and add continuation
            if len(line) > 120:
                # Try to break at logical points
                break_points = [" && ", " || ", " | ", " ; ", " \\"]
                for bp in break_points:
                    if bp in line:
                        parts = line.split(bp, 1)
                        if len(parts) == 2:
                            lines[line_idx] = parts[0] + bp.rstrip() + " \\"
                            lines.insert(line_idx + 1, "    " + parts[1])
                            return True

                # If no logical break point, break at space
                if " " in line:
                    last_space = line.rfind(" ", 0, 100)
                    if last_space > 0:
                        lines[line_idx] = line[:last_space] + " \\"
                        lines.insert(line_idx + 1, "    " + line[last_space + 1 :])
                        return True

        return False

    def _fix_missing_blank_lines(self, lines: list[str], line_idx: int) -> bool:
        """Fix missing blank lines before class/function definitions"""
        if line_idx < 2:
            return False

        # Check if we need to add blank lines
        current_line = lines[line_idx].strip()
        prev_line = lines[line_idx - 1].strip()
        prev_prev_line = lines[line_idx - 2].strip()

        if re.match(r"^(class|def)\s+", current_line) and prev_line and prev_prev_line:
            lines.insert(line_idx, "")
            lines.insert(line_idx, "")
            return True

        return False

    def _fix_one_line_import(self, lines: list[str], line_idx: int) -> bool:
        """Fix one-line imports by splitting them"""
        line = lines[line_idx].strip()

        if line.startswith("import "):
            # Handle: import a, b, c
            parts = line[7:].split(",")
            if len(parts) > 1:
                new_lines = ["import " + parts[0].strip()]
                for part in parts[1:]:
                    new_lines.append("import " + part.strip())

                lines[line_idx] = new_lines[0]
                for i, new_line in enumerate(new_lines[1:], 1):
                    lines.insert(line_idx + i, new_line)
                return True

        elif line.startswith("from ") and " import " in line:
            # Handle: from module import a, b, c
            from_part, import_part = line.split(" import ", 1)
            parts = import_part.split(",")
            if len(parts) > 1:
                new_lines = [from_part + " import " + parts[0].strip()]
                for part in parts[1:]:
                    new_lines.append("from " + from_part.split(" ")[1] + " import " + part.strip())

                lines[line_idx] = new_lines[0]
                for i, new_line in enumerate(new_lines[1:], 1):
                    lines.insert(line_idx + i, new_line)
                return True

        return False

    def _fix_unquoted_variable(self, lines: list[str], line_idx: int) -> bool:
        """Fix unquoted variables in shell scripts"""
        line = lines[line_idx]

        # Find and quote unquoted variables
        def quote_var(match):
            var = match.group(1)
            return f'"{var}"'

        new_line = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)(?=[^"\s])', quote_var, line)

        if new_line != line:
            lines[line_idx] = new_line
            return True

        return False


def main():
    """Main entry point for the one-liner linter"""
    parser = argparse.ArgumentParser(
        description="One-Liner Linter and Code Quality Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/one_liner_linter.py --scan .                    # Scan entire codebase
  python scripts/one_liner_linter.py --fix .                     # Fix issues automatically
  python scripts/one_liner_linter.py --report .                  # Generate detailed report
  python scripts/one_liner_linter.py --check-file path/to/file   # Check specific file
        """,
    )

    parser.add_argument("--scan", metavar="PATH", help="Scan codebase for linting issues")
    parser.add_argument("--fix", metavar="PATH", help="Automatically fix linting issues")
    parser.add_argument("--report", metavar="PATH", help="Generate detailed report")
    parser.add_argument("--check-file", metavar="FILE", help="Check specific file")
    parser.add_argument("--output", metavar="FILE", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not any([args.scan, args.fix, args.report, args.check_file]):
        parser.print_help()
        return 1

    # Initialize linter
    workspace_path = os.getcwd()
    linter = OneLinerLinter(workspace_path)

    try:
        if args.scan:
            print("🔍 Scanning codebase for linting issues...")
            summary = linter.scan_codebase(args.scan)

            if args.verbose:
                print("\n📋 Detailed Summary:")
                print(json.dumps(summary, indent=2))

        elif args.fix:
            print("🔧 Fixing linting issues automatically...")
            summary = linter.scan_codebase(args.fix)
            fixed_counts = linter.auto_fix_issues()

            if args.verbose:
                print("\n📋 Fix Summary:")
                print(json.dumps(fixed_counts, indent=2))

        elif args.report:
            print("📄 Generating detailed report...")
            summary = linter.scan_codebase(args.report)
            report = linter.generate_report(args.output)

            if not args.output:
                print("\n" + "=" * 80)
                print(report)
                print("=" * 80)

        elif args.check_file:
            print(f"🔍 Checking specific file: {args.check_file}")
            if not os.path.exists(args.check_file):
                print(f"❌ File not found: {args.check_file}")
                return 1

            linter._analyze_file(Path(args.check_file))
            summary = linter._generate_summary()

            print(f"\n📊 File Analysis Complete!")
            print(f"   Issues found: {summary['total_issues']}")
            print(f"   Critical: {summary['critical_count']}")
            print(f"   Warnings: {summary['warning_count']}")
            print(f"   Suggestions: {summary['suggestion_count']}")

            if args.verbose:
                for file_path, analysis in linter.file_analyses.items():
                    if analysis.total_issues > 0:
                        print(f"\n📁 {file_path}:")
                        for issue in analysis.issues:
                            print(f"   Line {issue.line_number}: {issue.description}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
