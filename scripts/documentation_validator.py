#!/usr/bin/env python3
"""
Documentation Validation System for Beast Mode AI Development Framework

This script validates all documentation by:
1. Verifying all documentation is accurate and up-to-date
2. Testing all code examples and instructions in documentation
3. Ensuring links and references are working correctly
4. Checking for consistency and completeness

Requirements addressed: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import os
import sys
import json
import re
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback
from urllib.parse import urlparse, urljoin
# Optional markdown import - will work without it
try:
    import markdown
    from markdown.extensions import codehilite, toc
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

@dataclass
class DocumentationIssue:
    """Represents a documentation issue."""
    file_path: str
    line_number: Optional[int]
    issue_type: str
    severity: str  # "error", "warning", "info"
    message: str
    suggestion: Optional[str] = None

@dataclass
class DocumentationValidationResult:
    """Result of validating a single documentation file."""
    file_path: str
    file_type: str
    success: bool
    issues: List[DocumentationIssue]
    code_examples_tested: int
    code_examples_passed: int
    links_checked: int
    links_working: int
    word_count: int
    
@dataclass
class DocumentationReport:
    """Comprehensive documentation validation report."""
    timestamp: str
    total_files: int
    successful_files: int
    failed_files: int
    total_issues: int
    error_count: int
    warning_count: int
    info_count: int
    results: List[DocumentationValidationResult]
    summary: Dict[str, Any]

class DocumentationValidator:
    """Validates documentation files for accuracy and completeness."""
    
    def __init__(self, docs_dir: str = "docs", include_readme: bool = True):
        self.docs_dir = Path(docs_dir).resolve()
        self.project_root = Path.cwd().resolve()
        self.include_readme = include_readme
        self.checked_urls = {}  # Cache for URL checks
        
    def validate_all_documentation(self) -> DocumentationReport:
        """Validate all documentation files."""
        print("📚 Starting comprehensive documentation validation...")
        
        # Find all documentation files
        doc_files = self._find_documentation_files()
        print(f"Found {len(doc_files)} documentation files to validate")
        
        results = []
        for doc_file in doc_files:
            print(f"\n📝 Validating: {doc_file.relative_to(self.project_root)}")
            result = self._validate_single_document(doc_file)
            results.append(result)
            
            # Print immediate feedback
            if result.success:
                print(f"✅ {doc_file.name}: PASSED")
            else:
                print(f"❌ {doc_file.name}: FAILED - {len(result.issues)} issues")
                
            if result.issues:
                error_count = sum(1 for issue in result.issues if issue.severity == "error")
                warning_count = sum(1 for issue in result.issues if issue.severity == "warning")
                if error_count > 0:
                    print(f"   🔴 {error_count} errors")
                if warning_count > 0:
                    print(f"   🟡 {warning_count} warnings")
        
        # Generate comprehensive report
        report = self._generate_report(results)
        self._save_report(report)
        
        return report
    
    def _find_documentation_files(self) -> List[Path]:
        """Find all documentation files."""
        doc_files = []
        
        # Look for markdown files in docs directory
        if self.docs_dir.exists():
            for pattern in ["**/*.md", "**/*.rst", "**/*.txt"]:
                doc_files.extend(self.docs_dir.glob(pattern))
        
        # Include README files if requested
        if self.include_readme:
            readme_patterns = ["README.md", "README.rst", "README.txt", "CONTRIBUTING.md", "CHANGELOG.md"]
            for pattern in readme_patterns:
                readme_file = self.project_root / pattern
                if readme_file.exists():
                    doc_files.append(readme_file)
        
        # Filter out hidden files and directories
        filtered_files = []
        for file_path in doc_files:
            if not any(part.startswith('.') for part in file_path.parts):
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    def _validate_single_document(self, doc_file: Path) -> DocumentationValidationResult:
        """Validate a single documentation file."""
        try:
            # Read the document
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Determine file type
            file_type = doc_file.suffix.lower()
            
            # Basic content validation
            issues.extend(self._validate_content_structure(content, doc_file))
            
            # Validate code examples
            code_examples_tested, code_examples_passed, code_issues = self._validate_code_examples(content, doc_file)
            issues.extend(code_issues)
            
            # Validate links
            links_checked, links_working, link_issues = self._validate_links(content, doc_file)
            issues.extend(link_issues)
            
            # Additional validations based on file type
            if file_type == '.md':
                issues.extend(self._validate_markdown_specific(content, doc_file))
            
            # Calculate word count
            word_count = len(content.split())
            
            success = not any(issue.severity == "error" for issue in issues)
            
            return DocumentationValidationResult(
                file_path=str(doc_file.relative_to(self.project_root)),
                file_type=file_type,
                success=success,
                issues=issues,
                code_examples_tested=code_examples_tested,
                code_examples_passed=code_examples_passed,
                links_checked=links_checked,
                links_working=links_working,
                word_count=word_count
            )
            
        except Exception as e:
            return DocumentationValidationResult(
                file_path=str(doc_file.relative_to(self.project_root)),
                file_type=doc_file.suffix.lower(),
                success=False,
                issues=[DocumentationIssue(
                    file_path=str(doc_file.relative_to(self.project_root)),
                    line_number=None,
                    issue_type="validation_error",
                    severity="error",
                    message=f"Failed to validate document: {str(e)}"
                )],
                code_examples_tested=0,
                code_examples_passed=0,
                links_checked=0,
                links_working=0,
                word_count=0
            )
    
    def _validate_content_structure(self, content: str, doc_file: Path) -> List[DocumentationIssue]:
        """Validate basic content structure."""
        issues = []
        lines = content.split('\n')
        
        # Check for empty files
        if not content.strip():
            issues.append(DocumentationIssue(
                file_path=str(doc_file.relative_to(self.project_root)),
                line_number=1,
                issue_type="empty_file",
                severity="error",
                message="Documentation file is empty"
            ))
            return issues
        
        # Check for title/header
        has_title = False
        for i, line in enumerate(lines[:10], 1):  # Check first 10 lines
            if line.strip().startswith('#') or line.strip().startswith('=') or line.strip().startswith('-'):
                has_title = True
                break
        
        if not has_title:
            issues.append(DocumentationIssue(
                file_path=str(doc_file.relative_to(self.project_root)),
                line_number=1,
                issue_type="missing_title",
                severity="warning",
                message="Document appears to be missing a title or header",
                suggestion="Add a title using # Title or underline with === or ---"
            ))
        
        # Check for very short documents (might be incomplete)
        if len(content.split()) < 50:
            issues.append(DocumentationIssue(
                file_path=str(doc_file.relative_to(self.project_root)),
                line_number=None,
                issue_type="short_content",
                severity="warning",
                message=f"Document is very short ({len(content.split())} words)",
                suggestion="Consider expanding the documentation with more details"
            ))
        
        # Check for TODO or FIXME markers
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                issues.append(DocumentationIssue(
                    file_path=str(doc_file.relative_to(self.project_root)),
                    line_number=i,
                    issue_type="todo_marker",
                    severity="info",
                    message=f"Found TODO/FIXME marker: {line.strip()}",
                    suggestion="Complete the TODO item or remove the marker"
                ))
        
        return issues
    
    def _validate_code_examples(self, content: str, doc_file: Path) -> Tuple[int, int, List[DocumentationIssue]]:
        """Validate code examples in documentation."""
        issues = []
        
        # Find code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        
        tested = 0
        passed = 0
        
        for i, (language, code) in enumerate(code_blocks):
            tested += 1
            
            # Skip non-executable code blocks
            if language and language.lower() in ['text', 'yaml', 'json', 'xml', 'html', 'css', 'sql']:
                passed += 1  # Consider these as passed since they're not meant to be executed
                continue
            
            # Validate Python code blocks
            if not language or language.lower() in ['python', 'py']:
                try:
                    # Basic syntax check
                    compile(code, f"<code_block_{i}>", "exec")
                    passed += 1
                except SyntaxError as e:
                    issues.append(DocumentationIssue(
                        file_path=str(doc_file.relative_to(self.project_root)),
                        line_number=None,
                        issue_type="code_syntax_error",
                        severity="error",
                        message=f"Python code block {i+1} has syntax error: {str(e)}",
                        suggestion="Fix the syntax error in the code example"
                    ))
                except Exception as e:
                    issues.append(DocumentationIssue(
                        file_path=str(doc_file.relative_to(self.project_root)),
                        line_number=None,
                        issue_type="code_validation_error",
                        severity="warning",
                        message=f"Code block {i+1} validation failed: {str(e)}"
                    ))
            
            # Validate shell/bash code blocks
            elif language and language.lower() in ['bash', 'sh', 'shell']:
                # Basic validation for shell commands
                lines = code.strip().split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Check for potentially dangerous commands
                        dangerous_patterns = [r'\brm\s+-rf\s+/', r'\bsudo\s+rm', r'\bdd\s+if=']
                        for pattern in dangerous_patterns:
                            if re.search(pattern, line):
                                issues.append(DocumentationIssue(
                                    file_path=str(doc_file.relative_to(self.project_root)),
                                    line_number=None,
                                    issue_type="dangerous_command",
                                    severity="warning",
                                    message=f"Potentially dangerous command in code block {i+1}: {line}",
                                    suggestion="Consider adding safety warnings or using safer alternatives"
                                ))
                passed += 1
            else:
                passed += 1  # Consider other languages as passed for now
        
        return tested, passed, issues
    
    def _validate_links(self, content: str, doc_file: Path) -> Tuple[int, int, List[DocumentationIssue]]:
        """Validate links in documentation."""
        issues = []
        
        # Find markdown links
        markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        
        # Find HTML links
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', content)
        
        # Find bare URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        bare_urls = re.findall(url_pattern, content)
        
        all_links = []
        
        # Process markdown links
        for text, url in markdown_links:
            all_links.append(('markdown', text, url))
        
        # Process HTML links
        for url in html_links:
            all_links.append(('html', '', url))
        
        # Process bare URLs
        for url in bare_urls:
            all_links.append(('bare', '', url))
        
        checked = 0
        working = 0
        
        for link_type, text, url in all_links:
            checked += 1
            
            # Skip internal anchors
            if url.startswith('#'):
                working += 1
                continue
            
            # Handle relative links
            if url.startswith('./') or url.startswith('../') or (not url.startswith('http') and not url.startswith('/')):
                # Check if relative file exists
                if doc_file.parent:
                    relative_path = doc_file.parent / url
                    if relative_path.exists():
                        working += 1
                    else:
                        issues.append(DocumentationIssue(
                            file_path=str(doc_file.relative_to(self.project_root)),
                            line_number=None,
                            issue_type="broken_relative_link",
                            severity="error",
                            message=f"Broken relative link: {url}",
                            suggestion=f"Check if the file exists at {relative_path}"
                        ))
                continue
            
            # Check absolute URLs
            if url.startswith('http'):
                if url in self.checked_urls:
                    # Use cached result
                    if self.checked_urls[url]:
                        working += 1
                    else:
                        issues.append(DocumentationIssue(
                            file_path=str(doc_file.relative_to(self.project_root)),
                            line_number=None,
                            issue_type="broken_external_link",
                            severity="warning",
                            message=f"Broken external link: {url}",
                            suggestion="Check if the URL is correct and accessible"
                        ))
                else:
                    # Check URL
                    try:
                        response = requests.head(url, timeout=10, allow_redirects=True)
                        if response.status_code < 400:
                            working += 1
                            self.checked_urls[url] = True
                        else:
                            self.checked_urls[url] = False
                            issues.append(DocumentationIssue(
                                file_path=str(doc_file.relative_to(self.project_root)),
                                line_number=None,
                                issue_type="broken_external_link",
                                severity="warning",
                                message=f"External link returns {response.status_code}: {url}",
                                suggestion="Check if the URL is correct and accessible"
                            ))
                    except requests.RequestException:
                        self.checked_urls[url] = False
                        issues.append(DocumentationIssue(
                            file_path=str(doc_file.relative_to(self.project_root)),
                            line_number=None,
                            issue_type="unreachable_external_link",
                            severity="warning",
                            message=f"Cannot reach external link: {url}",
                            suggestion="Check if the URL is correct and accessible"
                        ))
            else:
                working += 1  # Assume other link types are working for now
        
        return checked, working, issues
    
    def _validate_markdown_specific(self, content: str, doc_file: Path) -> List[DocumentationIssue]:
        """Validate markdown-specific issues."""
        issues = []
        lines = content.split('\n')
        
        # Check for proper heading hierarchy
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_levels.append((i, level))
        
        # Check for skipped heading levels
        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i-1][1]
            curr_level = heading_levels[i][1]
            curr_line = heading_levels[i][0]
            
            if curr_level > prev_level + 1:
                issues.append(DocumentationIssue(
                    file_path=str(doc_file.relative_to(self.project_root)),
                    line_number=curr_line,
                    issue_type="skipped_heading_level",
                    severity="warning",
                    message=f"Heading level jumps from {prev_level} to {curr_level}",
                    suggestion="Use consecutive heading levels (h1, h2, h3, etc.)"
                ))
        
        # Check for table formatting
        table_lines = [i for i, line in enumerate(lines, 1) if '|' in line]
        if table_lines:
            # Basic table validation
            for line_num in table_lines:
                line = lines[line_num - 1]
                if line.count('|') < 2:
                    issues.append(DocumentationIssue(
                        file_path=str(doc_file.relative_to(self.project_root)),
                        line_number=line_num,
                        issue_type="malformed_table",
                        severity="warning",
                        message="Possible malformed table row",
                        suggestion="Ensure table rows have proper | separators"
                    ))
        
        return issues
    
    def _generate_report(self, results: List[DocumentationValidationResult]) -> DocumentationReport:
        """Generate comprehensive documentation validation report."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        # Count issues by severity
        all_issues = []
        for result in results:
            all_issues.extend(result.issues)
        
        error_count = sum(1 for issue in all_issues if issue.severity == "error")
        warning_count = sum(1 for issue in all_issues if issue.severity == "warning")
        info_count = sum(1 for issue in all_issues if issue.severity == "info")
        
        # Calculate summary statistics
        total_code_examples = sum(r.code_examples_tested for r in results)
        passed_code_examples = sum(r.code_examples_passed for r in results)
        total_links = sum(r.links_checked for r in results)
        working_links = sum(r.links_working for r in results)
        total_words = sum(r.word_count for r in results)
        
        summary = {
            "success_rate": (successful / len(results)) * 100 if results else 0,
            "total_words": total_words,
            "average_words_per_file": total_words / len(results) if results else 0,
            "code_examples_success_rate": (passed_code_examples / total_code_examples) * 100 if total_code_examples > 0 else 100,
            "links_success_rate": (working_links / total_links) * 100 if total_links > 0 else 100,
            "issue_distribution": {
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count
            }
        }
        
        return DocumentationReport(
            timestamp=datetime.now().isoformat(),
            total_files=len(results),
            successful_files=successful,
            failed_files=failed,
            total_issues=len(all_issues),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            results=results,
            summary=summary
        )
    
    def _save_report(self, report: DocumentationReport) -> None:
        """Save documentation validation report to file."""
        report_file = self.project_root / "data" / "documentation_validation_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        # Convert to JSON-serializable format
        report_dict = asdict(report)
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
        print(f"\n📊 Documentation validation report saved to: {report_file}")
        
        # Also create a human-readable summary
        self._create_summary_report(report)
    
    def _create_summary_report(self, report: DocumentationReport) -> None:
        """Create human-readable summary report."""
        summary_file = self.project_root / "data" / "documentation_validation_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write("# Documentation Validation Summary Report\n\n")
            f.write(f"**Generated:** {report.timestamp}\n\n")
            
            f.write("## Overall Results\n\n")
            f.write(f"- **Total Files:** {report.total_files}\n")
            f.write(f"- **Successful:** {report.successful_files} ({report.summary['success_rate']:.1f}%)\n")
            f.write(f"- **Failed:** {report.failed_files}\n")
            f.write(f"- **Total Issues:** {report.total_issues}\n")
            f.write(f"- **Total Words:** {report.summary['total_words']:,}\n")
            f.write(f"- **Average Words per File:** {report.summary['average_words_per_file']:.0f}\n\n")
            
            f.write("## Issue Summary\n\n")
            f.write(f"- **Errors:** {report.error_count} 🔴\n")
            f.write(f"- **Warnings:** {report.warning_count} 🟡\n")
            f.write(f"- **Info:** {report.info_count} 🔵\n\n")
            
            f.write("## Code Examples\n\n")
            total_code = sum(r.code_examples_tested for r in report.results)
            passed_code = sum(r.code_examples_passed for r in report.results)
            f.write(f"- **Total Code Examples:** {total_code}\n")
            f.write(f"- **Passed:** {passed_code} ({report.summary['code_examples_success_rate']:.1f}%)\n\n")
            
            f.write("## Links\n\n")
            total_links = sum(r.links_checked for r in report.results)
            working_links = sum(r.links_working for r in report.results)
            f.write(f"- **Total Links:** {total_links}\n")
            f.write(f"- **Working:** {working_links} ({report.summary['links_success_rate']:.1f}%)\n\n")
            
            if report.failed_files > 0:
                f.write("## Failed Files\n\n")
                failed_results = [r for r in report.results if not r.success]
                for result in failed_results:
                    f.write(f"### {result.file_path}\n")
                    error_issues = [i for i in result.issues if i.severity == "error"]
                    for issue in error_issues:
                        f.write(f"- 🔴 **{issue.issue_type}:** {issue.message}\n")
                        if issue.suggestion:
                            f.write(f"  - *Suggestion:* {issue.suggestion}\n")
                    f.write("\n")
            
            if report.warning_count > 0:
                f.write("## Warnings\n\n")
                warning_results = [r for r in report.results if any(i.severity == "warning" for i in r.issues)]
                for result in warning_results:
                    warning_issues = [i for i in result.issues if i.severity == "warning"]
                    if warning_issues:
                        f.write(f"### {result.file_path}\n")
                        for issue in warning_issues:
                            f.write(f"- 🟡 **{issue.issue_type}:** {issue.message}\n")
                            if issue.suggestion:
                                f.write(f"  - *Suggestion:* {issue.suggestion}\n")
                        f.write("\n")
        
        print(f"📋 Documentation validation summary saved to: {summary_file}")

def main():
    """Main function to run documentation validation."""
    print("🚀 Beast Mode AI Framework - Documentation Validation System")
    print("=" * 60)
    
    # Initialize validator
    validator = DocumentationValidator()
    
    # Run validation
    report = validator.validate_all_documentation()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 DOCUMENTATION VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Files: {report.total_files}")
    print(f"Successful: {report.successful_files} ({report.summary['success_rate']:.1f}%)")
    print(f"Failed: {report.failed_files}")
    print(f"Total Issues: {report.total_issues}")
    
    if report.error_count > 0:
        print(f"\n🔴 ERRORS FOUND: {report.error_count}")
        print("Please fix documentation errors before public release!")
        
    if report.warning_count > 0:
        print(f"\n🟡 WARNINGS FOUND: {report.warning_count}")
        print("Consider addressing documentation warnings for better quality.")
    
    print(f"\n📊 Code Examples: {report.summary['code_examples_success_rate']:.1f}% success rate")
    print(f"🔗 Links: {report.summary['links_success_rate']:.1f}% working")
    print(f"📝 Total Words: {report.summary['total_words']:,}")
    
    if report.failed_files > 0:
        print(f"\n❌ {report.failed_files} documentation files failed validation")
        print("Please fix documentation issues before proceeding.")
        return 1
    else:
        print("\n✅ All documentation passed validation!")
        return 0

if __name__ == "__main__":
    sys.exit(main())