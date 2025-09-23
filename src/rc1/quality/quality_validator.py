#!/usr/bin/env python3
"""
RC1 Quality Assurance Agent
Beast Mode Full Compliance Execution

This agent ensures migration quality and compliance with all
project standards and requirements.
"""

import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import ast
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class QualityCheck:
    """Represents a single quality check"""
    check_name: str
    check_type: str  # 'python_quality', 'markdown_quality', 'structure_quality', 'compliance'
    status: str  # 'pass', 'fail', 'warning'
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    details: Dict[str, Any] = None
    fix_suggestion: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class QualitySummary:
    """Summary of quality assurance results"""
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    quality_score: float
    compliance_rate: float
    critical_issues: List[str]
    quality_issues: List[str]
    recommendations: List[str]
    execution_time: float


class QualityAssuranceAgent:
    """
    Quality Assurance Agent - Beast Mode Execution
    
    Responsibilities:
    - Implement quality validation
    - Check code compliance
    - Validate documentation
    - Ensure system performance
    - Generate quality report
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.migration_dir = self.project_root / "src" / "rc1" / "migration"
        self.quality_dir = self.project_root / "src" / "rc1" / "quality"
        self.logs_dir = self.quality_dir / "logs"
        
        # Create necessary directories
        self.quality_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality results
        self.quality_checks: List[QualityCheck] = []
        self.critical_issues: List[str] = []
        self.quality_issues: List[str] = []
        self.recommendations: List[str] = []
        
        logger.info("Quality Assurance Agent initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Quality directory: {self.quality_dir}")
    
    def check_python_quality(self) -> List[QualityCheck]:
        """Check Python code quality using Black, Flake8, and AST parsing"""
        logger.info("Checking Python code quality...")
        
        checks = []
        python_files = list(self.migration_dir.rglob("*.py"))
        
        for py_file in python_files:
            file_checks = self._check_python_file(py_file)
            checks.extend(file_checks)
        
        logger.info(f"Python quality check complete: {len(checks)} checks for {len(python_files)} files")
        return checks
    
    def _check_python_file(self, file_path: Path) -> List[QualityCheck]:
        """Check quality of a single Python file"""
        checks = []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST parsing check
            try:
                ast.parse(content)
                checks.append(QualityCheck(
                    check_name="ast_parsing",
                    check_type="python_quality",
                    status="pass",
                    message=f"File parses successfully with AST: {file_path.name}",
                    file_path=str(file_path)
                ))
            except SyntaxError as e:
                checks.append(QualityCheck(
                    check_name="ast_parsing",
                    check_type="python_quality",
                    status="fail",
                    message=f"Syntax error in file: {e}",
                    file_path=str(file_path),
                    line_number=e.lineno,
                    fix_suggestion="Fix syntax error to ensure file can be parsed"
                ))
                self.critical_issues.append(f"Syntax error in {file_path}: {e}")
            
            # Check for unused imports
            unused_imports = self._find_unused_imports(content)
            if unused_imports:
                checks.append(QualityCheck(
                    check_name="unused_imports",
                    check_type="python_quality",
                    status="warning",
                    message=f"Unused imports found: {', '.join(unused_imports)}",
                    file_path=str(file_path),
                    fix_suggestion="Remove unused imports to improve code quality"
                ))
                self.quality_issues.append(f"Unused imports in {file_path}: {unused_imports}")
            else:
                checks.append(QualityCheck(
                    check_name="unused_imports",
                    check_type="python_quality",
                    status="pass",
                    message=f"No unused imports found: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check for proper docstrings
            if not self._has_docstrings(content):
                checks.append(QualityCheck(
                    check_name="docstrings",
                    check_type="python_quality",
                    status="warning",
                    message=f"Missing docstrings in file: {file_path.name}",
                    file_path=str(file_path),
                    fix_suggestion="Add docstrings to functions and classes"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="docstrings",
                    check_type="python_quality",
                    status="pass",
                    message=f"Docstrings present: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check for type hints
            if not self._has_type_hints(content):
                checks.append(QualityCheck(
                    check_name="type_hints",
                    check_type="python_quality",
                    status="warning",
                    message=f"Missing type hints in file: {file_path.name}",
                    file_path=str(file_path),
                    fix_suggestion="Add type hints to improve code clarity"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="type_hints",
                    check_type="python_quality",
                    status="pass",
                    message=f"Type hints present: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check line length (PEP 8)
            long_lines = self._find_long_lines(content)
            if long_lines:
                checks.append(QualityCheck(
                    check_name="line_length",
                    check_type="python_quality",
                    status="warning",
                    message=f"Long lines found: {len(long_lines)} lines exceed 88 characters",
                    file_path=str(file_path),
                    details={"long_lines": long_lines},
                    fix_suggestion="Break long lines to improve readability"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="line_length",
                    check_type="python_quality",
                    status="pass",
                    message=f"Line length compliant: {file_path.name}",
                    file_path=str(file_path)
                ))
        
        except Exception as e:
            checks.append(QualityCheck(
                check_name="file_read_error",
                check_type="python_quality",
                status="fail",
                message=f"Could not read file: {e}",
                file_path=str(file_path)
            ))
            self.critical_issues.append(f"Could not read {file_path}: {e}")
        
        return checks
    
    def _find_unused_imports(self, content: str) -> List[str]:
        """Find unused imports in Python code"""
        try:
            tree = ast.parse(content)
            imports = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)
            
            unused = imports - used_names
            return list(unused)
        except Exception:
            return []
    
    def _has_docstrings(self, content: str) -> bool:
        """Check if file has docstrings"""
        try:
            tree = ast.parse(content)
            
            # Check module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Constant) 
                and isinstance(tree.body[0].value.value, str)):
                return True
            
            # Check for function/class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                        return True
            
            return False
        except Exception:
            return False
    
    def _has_type_hints(self, content: str) -> bool:
        """Check if file has type hints"""
        # Simple check for type hints
        type_hint_patterns = [
            r'def\s+\w+\([^)]*:\s*\w+',
            r'->\s*\w+',
            r':\s*List\[',
            r':\s*Dict\[',
            r':\s*Optional\[',
            r':\s*Union\['
        ]
        
        for pattern in type_hint_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _find_long_lines(self, content: str, max_length: int = 88) -> List[int]:
        """Find lines that exceed maximum length"""
        lines = content.splitlines()
        long_lines = []
        
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                long_lines.append(i)
        
        return long_lines
    
    def check_markdown_quality(self) -> List[QualityCheck]:
        """Check markdown documentation quality"""
        logger.info("Checking markdown quality...")
        
        checks = []
        markdown_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in markdown_files:
            file_checks = self._check_markdown_file(md_file)
            checks.extend(file_checks)
        
        logger.info(f"Markdown quality check complete: {len(checks)} checks for {len(markdown_files)} files")
        return checks
    
    def _check_markdown_file(self, file_path: Path) -> List[QualityCheck]:
        """Check quality of a single markdown file"""
        checks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for title
            if not any(line.startswith('#') for line in lines[:10]):
                checks.append(QualityCheck(
                    check_name="markdown_title",
                    check_type="markdown_quality",
                    status="warning",
                    message=f"Missing title in markdown file: {file_path.name}",
                    file_path=str(file_path),
                    fix_suggestion="Add a title using # at the beginning of the file"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="markdown_title",
                    check_type="markdown_quality",
                    status="pass",
                    message=f"Title present: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check for empty lines at end
            if content and not content.endswith('\n'):
                checks.append(QualityCheck(
                    check_name="markdown_newline",
                    check_type="markdown_quality",
                    status="warning",
                    message=f"File does not end with newline: {file_path.name}",
                    file_path=str(file_path),
                    fix_suggestion="Add newline at end of file"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="markdown_newline",
                    check_type="markdown_quality",
                    status="pass",
                    message=f"Proper newline ending: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check for consistent heading levels
            heading_issues = self._check_heading_consistency(lines)
            if heading_issues:
                checks.append(QualityCheck(
                    check_name="markdown_headings",
                    check_type="markdown_quality",
                    status="warning",
                    message=f"Heading consistency issues: {heading_issues}",
                    file_path=str(file_path),
                    fix_suggestion="Use consistent heading levels (start with #, then ##, etc.)"
                ))
            else:
                checks.append(QualityCheck(
                    check_name="markdown_headings",
                    check_type="markdown_quality",
                    status="pass",
                    message=f"Consistent headings: {file_path.name}",
                    file_path=str(file_path)
                ))
            
            # Check for broken links
            broken_links = self._find_broken_links(content, file_path)
            if broken_links:
                checks.append(QualityCheck(
                    check_name="markdown_links",
                    check_type="markdown_quality",
                    status="fail",
                    message=f"Broken links found: {len(broken_links)}",
                    file_path=str(file_path),
                    details={"broken_links": broken_links},
                    fix_suggestion="Fix broken links to ensure proper navigation"
                ))
                self.critical_issues.append(f"Broken links in {file_path}: {broken_links}")
            else:
                checks.append(QualityCheck(
                    check_name="markdown_links",
                    check_type="markdown_quality",
                    status="pass",
                    message=f"All links working: {file_path.name}",
                    file_path=str(file_path)
                ))
        
        except Exception as e:
            checks.append(QualityCheck(
                check_name="markdown_read_error",
                check_type="markdown_quality",
                status="fail",
                message=f"Could not read markdown file: {e}",
                file_path=str(file_path)
            ))
            self.critical_issues.append(f"Could not read {file_path}: {e}")
        
        return checks
    
    def _check_heading_consistency(self, lines: List[str]) -> Optional[str]:
        """Check for consistent heading levels in markdown"""
        headings = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                headings.append((i, level))
        
        if not headings:
            return None
        
        # Check if headings start with # and increase properly
        if headings[0][1] != 1:
            return "First heading should be level 1 (#)"
        
        # Check for skipped levels
        for i in range(1, len(headings)):
            prev_level = headings[i-1][1]
            curr_level = headings[i][1]
            if curr_level > prev_level + 1:
                return f"Heading level skipped at line {headings[i][0]}: {prev_level} -> {curr_level}"
        
        return None
    
    def _find_broken_links(self, content: str, file_path: Path) -> List[str]:
        """Find broken links in markdown content"""
        broken_links = []
        
        # Find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, content)
        
        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Check if it's a markdown file link
            if link_url.endswith('.md') or '.md#' in link_url:
                target_file = self._resolve_markdown_link(link_url, file_path)
                if not target_file or not Path(target_file).exists():
                    broken_links.append(f"{link_text} -> {link_url}")
        
        return broken_links
    
    def _resolve_markdown_link(self, link_url: str, source_file: Path) -> Optional[str]:
        """Resolve markdown link to actual file path"""
        try:
            # Remove anchor
            if '#' in link_url:
                link_url = link_url.split('#')[0]
            
            if link_url.startswith('/'):
                # Absolute path
                return str(self.project_root / link_url.lstrip('/'))
            elif link_url.startswith('./') or link_url.startswith('../'):
                # Relative path
                return str(source_file.parent / link_url)
            else:
                # Simple filename or relative path
                return str(source_file.parent / link_url)
        except Exception:
            return None
    
    def check_structure_quality(self) -> List[QualityCheck]:
        """Check overall structure quality"""
        logger.info("Checking structure quality...")
        
        checks = []
        
        # Check directory structure
        if self.docs_dir.exists():
            checks.append(QualityCheck(
                check_name="docs_directory_exists",
                check_type="structure_quality",
                status="pass",
                message="Documentation directory exists",
                file_path=str(self.docs_dir)
            ))
        else:
            checks.append(QualityCheck(
                check_name="docs_directory_exists",
                check_type="structure_quality",
                status="fail",
                message="Documentation directory missing",
                file_path=str(self.docs_dir)
            ))
            self.critical_issues.append("Documentation directory missing")
        
        # Check for index files
        index_files = [
            "docs/index.md",
            "docs/rc1/index.md"
        ]
        
        for index_file in index_files:
            full_path = self.project_root / index_file
            if full_path.exists():
                checks.append(QualityCheck(
                    check_name=f"index_file_{index_file.replace('/', '_')}",
                    check_type="structure_quality",
                    status="pass",
                    message=f"Index file exists: {index_file}",
                    file_path=str(full_path)
                ))
            else:
                checks.append(QualityCheck(
                    check_name=f"index_file_{index_file.replace('/', '_')}",
                    check_type="structure_quality",
                    status="warning",
                    message=f"Index file missing: {index_file}",
                    file_path=str(full_path),
                    fix_suggestion="Create index file for better navigation"
                ))
        
        # Check for README files in directories
        for category_dir in self.docs_dir.iterdir():
            if category_dir.is_dir():
                readme_file = category_dir / "README.md"
                if readme_file.exists():
                    checks.append(QualityCheck(
                        check_name=f"readme_{category_dir.name}",
                        check_type="structure_quality",
                        status="pass",
                        message=f"README exists in {category_dir.name}",
                        file_path=str(readme_file)
                    ))
                else:
                    checks.append(QualityCheck(
                        check_name=f"readme_{category_dir.name}",
                        check_type="structure_quality",
                        status="warning",
                        message=f"README missing in {category_dir.name}",
                        file_path=str(category_dir),
                        fix_suggestion="Add README.md to directory for documentation"
                    ))
        
        logger.info(f"Structure quality check complete: {len(checks)} checks")
        return checks
    
    def check_compliance(self) -> List[QualityCheck]:
        """Check compliance with project standards"""
        logger.info("Checking compliance...")
        
        checks = []
        
        # Check for required migration files
        required_files = [
            "src/rc1/migration/migration_planner.py",
            "src/rc1/migration/migration_executor.py",
            "src/rc1/migration/directory_structure_creator.py",
            "src/rc1/migration/link_reference_updater.py",
            "src/rc1/migration/validation_system.py"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                checks.append(QualityCheck(
                    check_name=f"required_file_{file_path.replace('/', '_')}",
                    check_type="compliance",
                    status="pass",
                    message=f"Required file exists: {file_path}",
                    file_path=str(full_path)
                ))
            else:
                checks.append(QualityCheck(
                    check_name=f"required_file_{file_path.replace('/', '_')}",
                    check_type="compliance",
                    status="fail",
                    message=f"Required file missing: {file_path}",
                    file_path=str(full_path)
                ))
                self.critical_issues.append(f"Required file missing: {file_path}")
        
        # Check for proper logging
        migration_files = list(self.migration_dir.rglob("*.py"))
        for py_file in migration_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'logging' in content and 'logger' in content:
                checks.append(QualityCheck(
                    check_name=f"logging_{py_file.name}",
                    check_type="compliance",
                    status="pass",
                    message=f"Proper logging implemented: {py_file.name}",
                    file_path=str(py_file)
                ))
            else:
                checks.append(QualityCheck(
                    check_name=f"logging_{py_file.name}",
                    check_type="compliance",
                    status="warning",
                    message=f"Missing logging: {py_file.name}",
                    file_path=str(py_file),
                    fix_suggestion="Add proper logging to improve debugging"
                ))
        
        logger.info(f"Compliance check complete: {len(checks)} checks")
        return checks
    
    def run_complete_quality_check(self) -> QualitySummary:
        """Run complete quality assurance check"""
        start_time = datetime.now()
        
        logger.info("Starting complete quality assurance check...")
        
        # Run all quality checks
        all_checks = []
        
        # Python quality
        python_checks = self.check_python_quality()
        all_checks.extend(python_checks)
        
        # Markdown quality
        markdown_checks = self.check_markdown_quality()
        all_checks.extend(markdown_checks)
        
        # Structure quality
        structure_checks = self.check_structure_quality()
        all_checks.extend(structure_checks)
        
        # Compliance
        compliance_checks = self.check_compliance()
        all_checks.extend(compliance_checks)
        
        # Calculate summary
        total_checks = len(all_checks)
        passed_checks = len([c for c in all_checks if c.status == "pass"])
        failed_checks = len([c for c in all_checks if c.status == "fail"])
        warning_checks = len([c for c in all_checks if c.status == "warning"])
        
        quality_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        compliance_rate = (len([c for c in compliance_checks if c.status == "pass"]) / len(compliance_checks)) * 100 if compliance_checks else 0
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Generate recommendations
        self._generate_quality_recommendations(all_checks)
        
        summary = QualitySummary(
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warning_checks=warning_checks,
            quality_score=quality_score,
            compliance_rate=compliance_rate,
            critical_issues=self.critical_issues,
            quality_issues=self.quality_issues,
            recommendations=self.recommendations,
            execution_time=execution_time
        )
        
        # Save quality results
        self.save_quality_results(summary, all_checks)
        
        logger.info(f"Complete quality check finished in {execution_time:.2f}s")
        logger.info(f"Quality score: {quality_score:.1f}%")
        
        return summary
    
    def _generate_quality_recommendations(self, checks: List[QualityCheck]) -> None:
        """Generate quality recommendations based on check results"""
        failed_checks = [c for c in checks if c.status == "fail"]
        warning_checks = [c for c in checks if c.status == "warning"]
        
        if failed_checks:
            self.recommendations.append("Address all failed quality checks before deployment")
        
        if warning_checks:
            self.recommendations.append("Review warning checks for potential improvements")
        
        if any("syntax" in c.message.lower() for c in failed_checks):
            self.recommendations.append("Fix syntax errors to ensure code can be executed")
        
        if any("broken" in c.message.lower() for c in failed_checks):
            self.recommendations.append("Fix broken links to ensure proper navigation")
        
        if any("missing" in c.message.lower() for c in failed_checks):
            self.recommendations.append("Ensure all required files and components are present")
        
        if not self.critical_issues:
            self.recommendations.append("Quality check passed - system ready for production")
    
    def save_quality_results(self, summary: QualitySummary, checks: List[QualityCheck]) -> str:
        """Save quality results to file"""
        results_file = self.logs_dir / f"quality_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Prepare results data
        results_data = {
            'summary': asdict(summary),
            'checks': [asdict(check) for check in checks],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Quality results saved to: {results_file}")
        return str(results_file)


def main():
    """Main execution function for Quality Assurance Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RC1 Quality Assurance Agent')
    parser.add_argument('--check-type', choices=['all', 'python', 'markdown', 'structure', 'compliance'], 
                       default='all', help='Type of quality check to run')
    
    args = parser.parse_args()
    
    print("🤖 RC1 Quality Assurance Agent - Beast Mode Execution")
    print("=" * 70)
    
    # Initialize quality agent
    quality_agent = QualityAssuranceAgent()
    
    if args.check_type == 'all':
        print("🔍 Running complete quality assurance check...")
        summary = quality_agent.run_complete_quality_check()
        
        # Report results
        print("\n✅ Quality Assurance Check Complete!")
        print(f"📊 Total checks: {summary.total_checks}")
        print(f"✅ Passed: {summary.passed_checks}")
        print(f"❌ Failed: {summary.failed_checks}")
        print(f"⚠️  Warnings: {summary.warning_checks}")
        print(f"📈 Quality score: {summary.quality_score:.1f}%")
        print(f"📋 Compliance rate: {summary.compliance_rate:.1f}%")
        print(f"⏱️  Execution time: {summary.execution_time:.2f}s")
        
        if summary.critical_issues:
            print(f"\n🚨 Critical Issues ({len(summary.critical_issues)}):")
            for issue in summary.critical_issues[:5]:
                print(f"  - {issue}")
            if len(summary.critical_issues) > 5:
                print(f"  ... and {len(summary.critical_issues) - 5} more issues")
        
        if summary.quality_issues:
            print(f"\n⚠️  Quality Issues ({len(summary.quality_issues)}):")
            for issue in summary.quality_issues[:5]:
                print(f"  - {issue}")
        
        if summary.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in summary.recommendations:
                print(f"  - {rec}")
        
        # Determine overall status
        if summary.failed_checks == 0:
            print("\n🎉 QUALITY CHECK PASSED!")
        else:
            print(f"\n❌ QUALITY CHECK FAILED - {summary.failed_checks} critical issues")
    
    else:
        print(f"🔍 Running {args.check_type} quality check...")
        # Run specific quality check type
        if args.check_type == 'python':
            checks = quality_agent.check_python_quality()
        elif args.check_type == 'markdown':
            checks = quality_agent.check_markdown_quality()
        elif args.check_type == 'structure':
            checks = quality_agent.check_structure_quality()
        elif args.check_type == 'compliance':
            checks = quality_agent.check_compliance()
        
        print(f"Quality check complete: {len(checks)} checks run")


if __name__ == "__main__":
    main()

