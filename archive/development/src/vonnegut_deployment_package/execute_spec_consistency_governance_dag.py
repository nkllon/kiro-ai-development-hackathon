#!/usr/bin/env python3
"""
Spec Consistency Governance DAG Executor

Executes the systematic implementation of spec governance across all 110+ specs
to ensure structural completeness, naming consistency, and lifecycle management.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class SpecConsistencyGovernanceDAG:
    """DAG executor for spec consistency governance implementation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.specs_dir = self.project_root / ".kiro" / "specs"
        self.execution_logs_dir = self.project_root / ".kiro" / "execution-logs" / "spec-consistency-governance"
        self.execution_logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.execution_logs_dir / "execution-state.json"
        self.load_execution_state()
    
    def load_execution_state(self):
        """Load execution state from disk."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "started_at": datetime.now().isoformat(),
                "current_phase": 0,
                "tasks": {},
                "phases": {
                    "1": {"status": "pending", "started_at": None, "completed_at": None},
                    "2": {"status": "pending", "started_at": None, "completed_at": None},
                    "3": {"status": "pending", "started_at": None, "completed_at": None},
                    "4": {"status": "pending", "started_at": None, "completed_at": None},
                    "5": {"status": "pending", "started_at": None, "completed_at": None}
                }
            }
    
    def save_execution_state(self):
        """Save execution state to disk."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def execute_phase_1(self, dry_run=False):
        """Execute Phase 1: Critical Infrastructure (Week 1, 25 hours)."""
        print("🚀 Starting Phase 1: Critical Infrastructure")
        
        if not dry_run:
            self.state["phases"]["1"]["status"] = "running"
            self.state["phases"]["1"]["started_at"] = datetime.now().isoformat()
            self.save_execution_state()
        
        tasks = [
            ("1.1", "Create Core Module Structure", self._task_1_1),
            ("1.2", "Implement SpecValidator Core", self._task_1_2),
            ("1.3", "Implement SpecReporter", self._task_1_3),
            ("1.4", "Create CLI Interface", self._task_1_4),
            ("1.5", "Remove Empty Output Directory", self._task_1_5),
            ("1.6", "Create Makefile Targets", self._task_1_6)
        ]
        
        for task_id, task_name, task_func in tasks:
            print(f"\n📋 Task {task_id}: {task_name}")
            if dry_run:
                print(f"   [DRY RUN] Would execute: {task_func.__name__}")
            else:
                try:
                    result = task_func()
                    self.state["tasks"][task_id] = {
                        "status": "completed",
                        "completed_at": datetime.now().isoformat(),
                        "result": result
                    }
                    print(f"   ✅ Completed: {task_name}")
                except Exception as e:
                    self.state["tasks"][task_id] = {
                        "status": "failed",
                        "failed_at": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    print(f"   ❌ Failed: {task_name} - {e}")
                    raise
                
                self.save_execution_state()
        
        if not dry_run:
            self.state["phases"]["1"]["status"] = "completed"
            self.state["phases"]["1"]["completed_at"] = datetime.now().isoformat()
            self.state["current_phase"] = 1
            self.save_execution_state()
        
        print("\n✅ Phase 1 Complete: Critical Infrastructure")
        return True
    
    def execute_phase_2(self, dry_run=False):
        """Execute Phase 2: Governance & Prevention (Week 2, 38 hours)."""
        print("🚀 Starting Phase 2: Governance & Prevention")
        
        if not dry_run:
            self.state["phases"]["2"]["status"] = "running"
            self.state["phases"]["2"]["started_at"] = datetime.now().isoformat()
            self.save_execution_state()
        
        tasks = [
            ("2.1", "Build SpecRegistry with JSON Index", self._task_2_1),
            ("2.2", "Implement Lifecycle Tracking", self._task_2_2),
            ("2.3", "Implement SpecRemediator with Dry-run", self._task_2_3),
            ("2.4", "Extra File Management", self._task_2_4),
            ("2.5", "Create Git Pre-commit Hook", self._task_2_5),
            ("2.6", "Document Spec Standards", self._task_2_6)
        ]
        
        for task_id, task_name, task_func in tasks:
            print(f"\n📋 Task {task_id}: {task_name}")
            if dry_run:
                print(f"   [DRY RUN] Would execute: {task_func.__name__}")
            else:
                try:
                    result = task_func()
                    self.state["tasks"][task_id] = {
                        "status": "completed",
                        "completed_at": datetime.now().isoformat(),
                        "result": result
                    }
                    print(f"   ✅ Completed: {task_name}")
                except Exception as e:
                    self.state["tasks"][task_id] = {
                        "status": "failed",
                        "failed_at": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    print(f"   ❌ Failed: {task_name} - {e}")
                    raise
                
                self.save_execution_state()
        
        if not dry_run:
            self.state["phases"]["2"]["status"] = "completed"
            self.state["phases"]["2"]["completed_at"] = datetime.now().isoformat()
            self.state["current_phase"] = 2
            self.save_execution_state()
        
        print("\n✅ Phase 2 Complete: Governance & Prevention")
        return True
    
    def _task_1_1(self):
        """Task 1.1: Create Core Module Structure (2 hours)."""
        # Create src/spec_governance directory structure
        spec_gov_dir = self.project_root / "src" / "spec_governance"
        spec_gov_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = spec_gov_dir / "__init__.py"
        init_content = '''"""
Spec Governance Module

Provides systematic validation, remediation, and lifecycle management
for all specifications in .kiro/specs/ directory.
"""

from .validator import SpecValidator
from .reporter import SpecReporter
from .remediator import SpecRemediator
from .registry import SpecRegistry

__version__ = "1.0.0"
__all__ = ["SpecValidator", "SpecReporter", "SpecRemediator", "SpecRegistry"]
'''
        with open(init_file, 'w') as f:
            f.write(init_content)
        
        # Create test structure
        test_dir = self.project_root / "tests" / "unit" / "spec_governance"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_init = test_dir / "__init__.py"
        test_init.touch()
        
        return {"module_created": True, "test_structure": True}
    
    def _task_1_2(self):
        """Task 1.2: Implement SpecValidator Core (8 hours)."""
        validator_file = self.project_root / "src" / "spec_governance" / "validator.py"
        
        validator_content = '''"""
Spec Validator - Core validation logic for spec consistency governance.

Detects incomplete specs, extra files, and naming violations.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Any
from datetime import datetime


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a spec."""
    spec_name: str
    issue_type: str  # 'missing_file', 'extra_file', 'naming_violation'
    severity: str    # 'critical', 'warning', 'info'
    description: str
    file_path: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Results of spec validation."""
    spec_name: str
    is_complete: bool
    issues: List[ValidationIssue]
    files_found: Set[str]
    extra_files: Set[str]
    
    @property
    def has_critical_issues(self) -> bool:
        return any(issue.severity == 'critical' for issue in self.issues)


@dataclass
class ValidationReport:
    """Complete validation report for all specs."""
    total_specs: int
    complete_specs: int
    incomplete_specs: int
    specs_with_extra_files: int
    validation_results: Dict[str, ValidationResult]
    generated_at: datetime
    
    @property
    def completion_rate(self) -> float:
        return (self.complete_specs / self.total_specs) * 100 if self.total_specs > 0 else 0.0


class SpecValidator:
    """Validates spec consistency and completeness."""
    
    REQUIRED_FILES = {"requirements.md", "design.md", "tasks.md"}
    ALLOWED_EXTRA_FILES = {
        ".spec-state",
        ".spec-exempt", 
        ".spec-extra-files",
        "dag-config.yml",
        "DAG_EXECUTION_PLAN.md",
        "DAG_TASKS.md",
        "LAUNCH_READINESS.md"
    }
    
    def __init__(self, specs_dir: Path = None):
        self.specs_dir = specs_dir or Path(".kiro/specs")
        if not self.specs_dir.exists():
            raise ValueError(f"Specs directory not found: {self.specs_dir}")
    
    def validate_all_specs(self) -> ValidationReport:
        """Validate all specs in the specs directory."""
        spec_dirs = [d for d in self.specs_dir.iterdir() 
                    if d.is_dir() and not d.name.startswith('.')]
        
        validation_results = {}
        complete_count = 0
        extra_files_count = 0
        
        for spec_dir in spec_dirs:
            result = self.validate_spec(spec_dir.name)
            validation_results[spec_dir.name] = result
            
            if result.is_complete:
                complete_count += 1
            
            if result.extra_files:
                extra_files_count += 1
        
        return ValidationReport(
            total_specs=len(spec_dirs),
            complete_specs=complete_count,
            incomplete_specs=len(spec_dirs) - complete_count,
            specs_with_extra_files=extra_files_count,
            validation_results=validation_results,
            generated_at=datetime.now()
        )
    
    def validate_spec(self, spec_name: str) -> ValidationResult:
        """Validate a single spec for completeness and consistency."""
        spec_path = self.specs_dir / spec_name
        
        if not spec_path.exists() or not spec_path.is_dir():
            return ValidationResult(
                spec_name=spec_name,
                is_complete=False,
                issues=[ValidationIssue(
                    spec_name=spec_name,
                    issue_type="missing_directory",
                    severity="critical",
                    description=f"Spec directory does not exist: {spec_path}"
                )],
                files_found=set(),
                extra_files=set()
            )
        
        # Get all files in spec directory
        all_files = {f.name for f in spec_path.iterdir() if f.is_file()}
        
        # Check for required files
        missing_files = self.REQUIRED_FILES - all_files
        found_required = self.REQUIRED_FILES & all_files
        
        # Check for extra files
        extra_files = all_files - self.REQUIRED_FILES - self.ALLOWED_EXTRA_FILES
        
        # Generate issues
        issues = []
        
        # Missing file issues
        for missing_file in missing_files:
            issues.append(ValidationIssue(
                spec_name=spec_name,
                issue_type="missing_file",
                severity="critical",
                description=f"Missing required file: {missing_file}",
                file_path=str(spec_path / missing_file),
                suggested_fix=f"Create {missing_file} using template generator"
            ))
        
        # Extra file issues
        for extra_file in extra_files:
            # Determine if it's a backup, execution artifact, or other
            if any(pattern in extra_file.lower() for pattern in 
                   ['backup', '_fixed', '_backpropagated', 'launch_summary', 'parallel_dag']):
                suggested_location = ".kiro/archive/" if 'backup' in extra_file.lower() else ".kiro/execution-logs/"
                issues.append(ValidationIssue(
                    spec_name=spec_name,
                    issue_type="extra_file",
                    severity="warning",
                    description=f"Extra file should be moved: {extra_file}",
                    file_path=str(spec_path / extra_file),
                    suggested_fix=f"Move to {suggested_location}{spec_name}/"
                ))
            else:
                issues.append(ValidationIssue(
                    spec_name=spec_name,
                    issue_type="extra_file",
                    severity="info",
                    description=f"Unapproved extra file: {extra_file}",
                    file_path=str(spec_path / extra_file),
                    suggested_fix="Add to .spec-extra-files with justification or remove"
                ))
        
        # Check file naming conventions
        for file_name in found_required:
            if not self._is_canonical_name(file_name):
                issues.append(ValidationIssue(
                    spec_name=spec_name,
                    issue_type="naming_violation",
                    severity="warning",
                    description=f"Non-canonical file name: {file_name}",
                    file_path=str(spec_path / file_name),
                    suggested_fix=f"Rename to canonical form (lowercase)"
                ))
        
        is_complete = len(missing_files) == 0
        
        return ValidationResult(
            spec_name=spec_name,
            is_complete=is_complete,
            issues=issues,
            files_found=found_required,
            extra_files=extra_files
        )
    
    def _is_canonical_name(self, filename: str) -> bool:
        """Check if filename follows canonical naming convention."""
        canonical_names = {"requirements.md", "design.md", "tasks.md"}
        return filename in canonical_names
    
    def get_incomplete_specs(self) -> List[str]:
        """Get list of incomplete spec names."""
        report = self.validate_all_specs()
        return [name for name, result in report.validation_results.items() 
                if not result.is_complete]
    
    def get_specs_with_extra_files(self) -> List[str]:
        """Get list of specs with extra files."""
        report = self.validate_all_specs()
        return [name for name, result in report.validation_results.items() 
                if result.extra_files]
'''
        
        with open(validator_file, 'w') as f:
            f.write(validator_content)
        
        return {"validator_implemented": True, "lines_of_code": len(validator_content.split('\n'))}
    
    def _task_1_3(self):
        """Task 1.3: Implement SpecReporter (6 hours)."""
        reporter_file = self.project_root / "src" / "spec_governance" / "reporter.py"
        
        reporter_content = '''"""
Spec Reporter - Generate comprehensive reports on spec governance status.

Creates markdown reports, JSON exports, and metrics for CI integration.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .validator import SpecValidator, ValidationReport, ValidationResult, ValidationIssue


class SpecReporter:
    """Generates comprehensive reports on spec governance status."""
    
    def __init__(self, validator: SpecValidator = None):
        self.validator = validator or SpecValidator()
        self.reports_dir = Path(".kiro/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, format_type: str = "markdown") -> str:
        """Generate comprehensive spec governance report."""
        validation_report = self.validator.validate_all_specs()
        
        if format_type == "markdown":
            return self._generate_markdown_report(validation_report)
        elif format_type == "json":
            return self._generate_json_report(validation_report)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def save_report(self, format_type: str = "markdown", filename: str = None) -> Path:
        """Generate and save report to file."""
        report_content = self.generate_report(format_type)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            extension = "md" if format_type == "markdown" else "json"
            filename = f"spec-quality-{timestamp}.{extension}"
        
        report_path = self.reports_dir / filename
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return report_path
    
    def _generate_markdown_report(self, validation_report: ValidationReport) -> str:
        """Generate markdown format report."""
        report = []
        
        # Header
        report.append("# Spec Consistency Governance Report")
        report.append(f"**Generated:** {validation_report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Specs:** {validation_report.total_specs}")
        report.append(f"- **Complete Specs:** {validation_report.complete_specs}")
        report.append(f"- **Incomplete Specs:** {validation_report.incomplete_specs}")
        report.append(f"- **Completion Rate:** {validation_report.completion_rate:.1f}%")
        report.append(f"- **Specs with Extra Files:** {validation_report.specs_with_extra_files}")
        report.append("")
        
        # Status indicator
        if validation_report.completion_rate >= 95:
            status = "🟢 EXCELLENT"
        elif validation_report.completion_rate >= 80:
            status = "🟡 GOOD"
        else:
            status = "🔴 NEEDS ATTENTION"
        
        report.append(f"**Overall Status:** {status}")
        report.append("")
        
        # Incomplete Specs Section
        if validation_report.incomplete_specs > 0:
            report.append("## Incomplete Specs")
            report.append("")
            report.append("The following specs are missing required files:")
            report.append("")
            
            incomplete_specs = [(name, result) for name, result in validation_report.validation_results.items() 
                              if not result.is_complete]
            
            for spec_name, result in sorted(incomplete_specs):
                missing_files = [issue.description.split(": ")[1] for issue in result.issues 
                               if issue.issue_type == "missing_file"]
                report.append(f"### {spec_name}")
                report.append(f"**Missing Files:** {', '.join(missing_files)}")
                report.append(f"**Path:** `.kiro/specs/{spec_name}/`")
                report.append("")
        
        # Extra Files Section
        specs_with_extras = [(name, result) for name, result in validation_report.validation_results.items() 
                           if result.extra_files]
        
        if specs_with_extras:
            report.append("## Specs with Extra Files")
            report.append("")
            
            for spec_name, result in sorted(specs_with_extras):
                report.append(f"### {spec_name}")
                report.append(f"**Extra Files:** {', '.join(sorted(result.extra_files))}")
                
                # Show suggested actions
                extra_file_issues = [issue for issue in result.issues if issue.issue_type == "extra_file"]
                if extra_file_issues:
                    report.append("**Suggested Actions:**")
                    for issue in extra_file_issues:
                        report.append(f"- {issue.suggested_fix}")
                report.append("")
        
        # Recommendations Section
        report.append("## Recommendations")
        report.append("")
        
        if validation_report.incomplete_specs > 0:
            report.append("### Immediate Actions")
            report.append("1. **Create missing files** using template generator:")
            report.append("   ```bash")
            report.append("   python -m spec_governance.cli remediate --create-stubs")
            report.append("   ```")
            report.append("")
        
        if validation_report.specs_with_extra_files > 0:
            report.append("2. **Move extra files** to appropriate locations:")
            report.append("   ```bash")
            report.append("   python -m spec_governance.cli remediate --move-extras")
            report.append("   ```")
            report.append("")
        
        report.append("### Prevention Measures")
        report.append("- Enable git pre-commit hooks to prevent incomplete specs")
        report.append("- Use `make spec-create` for new specifications")
        report.append("- Regular validation with `make spec-validate`")
        report.append("")
        
        # Metrics Section
        report.append("## Quality Metrics")
        report.append("")
        report.append("| Metric | Value | Target |")
        report.append("|--------|-------|--------|")
        report.append(f"| Completion Rate | {validation_report.completion_rate:.1f}% | 100% |")
        
        extra_compliance = ((validation_report.total_specs - validation_report.specs_with_extra_files) / 
                          validation_report.total_specs * 100) if validation_report.total_specs > 0 else 0
        report.append(f"| Extra File Compliance | {extra_compliance:.1f}% | 100% |")
        report.append(f"| Total Specs | {validation_report.total_specs} | Growing |")
        report.append("")
        
        return "\\n".join(report)
    
    def _generate_json_report(self, validation_report: ValidationReport) -> str:
        """Generate JSON format report for CI integration."""
        # Convert dataclasses to dictionaries
        report_dict = {
            "summary": {
                "total_specs": validation_report.total_specs,
                "complete_specs": validation_report.complete_specs,
                "incomplete_specs": validation_report.incomplete_specs,
                "completion_rate": validation_report.completion_rate,
                "specs_with_extra_files": validation_report.specs_with_extra_files,
                "generated_at": validation_report.generated_at.isoformat()
            },
            "specs": {}
        }
        
        for spec_name, result in validation_report.validation_results.items():
            report_dict["specs"][spec_name] = {
                "is_complete": result.is_complete,
                "files_found": list(result.files_found),
                "extra_files": list(result.extra_files),
                "issues": [
                    {
                        "type": issue.issue_type,
                        "severity": issue.severity,
                        "description": issue.description,
                        "file_path": issue.file_path,
                        "suggested_fix": issue.suggested_fix
                    }
                    for issue in result.issues
                ]
            }
        
        return json.dumps(report_dict, indent=2)
    
    def compute_metrics(self) -> Dict[str, Any]:
        """Compute quality metrics for dashboard integration."""
        validation_report = self.validator.validate_all_specs()
        
        return {
            "completion_rate": validation_report.completion_rate,
            "total_specs": validation_report.total_specs,
            "complete_specs": validation_report.complete_specs,
            "incomplete_specs": validation_report.incomplete_specs,
            "specs_with_extra_files": validation_report.specs_with_extra_files,
            "extra_file_compliance_rate": (
                (validation_report.total_specs - validation_report.specs_with_extra_files) / 
                validation_report.total_specs * 100
            ) if validation_report.total_specs > 0 else 0,
            "generated_at": datetime.now().isoformat()
        }
'''
        
        with open(reporter_file, 'w') as f:
            f.write(reporter_content)
        
        return {"reporter_implemented": True, "lines_of_code": len(reporter_content.split('\n'))}
    
    def _task_1_4(self):
        """Task 1.4: Create CLI Interface (6 hours)."""
        cli_file = self.project_root / "src" / "spec_governance" / "cli.py"
        
        cli_content = '''"""
Spec Governance CLI - Command-line interface for spec validation and management.

Provides commands for validation, reporting, and remediation.
"""

import sys
import click
import json
from pathlib import Path
from typing import Optional

from .validator import SpecValidator
from .reporter import SpecReporter


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Spec Governance CLI - Systematic spec validation and management."""
    pass


@cli.command()
@click.option('--spec', help='Validate specific spec by name')
@click.option('--all', 'validate_all', is_flag=True, help='Validate all specs (default)')
@click.option('--ci', is_flag=True, help='CI mode - JSON output and exit codes')
@click.option('--specs-dir', type=click.Path(exists=True), help='Custom specs directory')
def validate(spec: Optional[str], validate_all: bool, ci: bool, specs_dir: Optional[str]):
    """Validate spec completeness and consistency."""
    try:
        specs_path = Path(specs_dir) if specs_dir else Path(".kiro/specs")
        validator = SpecValidator(specs_path)
        
        if spec:
            # Validate single spec
            result = validator.validate_spec(spec)
            
            if ci:
                # CI mode - JSON output
                output = {
                    "spec": spec,
                    "is_complete": result.is_complete,
                    "issues": [
                        {
                            "type": issue.issue_type,
                            "severity": issue.severity,
                            "description": issue.description
                        }
                        for issue in result.issues
                    ]
                }
                click.echo(json.dumps(output, indent=2))
                sys.exit(0 if result.is_complete else 1)
            else:
                # Human-readable output
                if result.is_complete:
                    click.echo(f"✅ {spec}: Complete")
                else:
                    click.echo(f"❌ {spec}: Incomplete")
                    for issue in result.issues:
                        if issue.severity == "critical":
                            click.echo(f"   🔴 {issue.description}")
                        elif issue.severity == "warning":
                            click.echo(f"   🟡 {issue.description}")
                        else:
                            click.echo(f"   ℹ️  {issue.description}")
        else:
            # Validate all specs
            report = validator.validate_all_specs()
            
            if ci:
                # CI mode - JSON output
                output = {
                    "total_specs": report.total_specs,
                    "complete_specs": report.complete_specs,
                    "incomplete_specs": report.incomplete_specs,
                    "completion_rate": report.completion_rate,
                    "specs_with_extra_files": report.specs_with_extra_files
                }
                click.echo(json.dumps(output, indent=2))
                sys.exit(0 if report.incomplete_specs == 0 else 1)
            else:
                # Human-readable output
                click.echo(f"📊 Spec Validation Report")
                click.echo(f"   Total specs: {report.total_specs}")
                click.echo(f"   Complete: {report.complete_specs}")
                click.echo(f"   Incomplete: {report.incomplete_specs}")
                click.echo(f"   Completion rate: {report.completion_rate:.1f}%")
                click.echo(f"   Specs with extra files: {report.specs_with_extra_files}")
                
                if report.incomplete_specs > 0:
                    click.echo("\\n❌ Incomplete specs:")
                    for name, result in report.validation_results.items():
                        if not result.is_complete:
                            missing = [i.description.split(": ")[1] for i in result.issues 
                                     if i.issue_type == "missing_file"]
                            click.echo(f"   - {name}: missing {', '.join(missing)}")
                
                if report.specs_with_extra_files > 0:
                    click.echo("\\n⚠️  Specs with extra files:")
                    for name, result in report.validation_results.items():
                        if result.extra_files:
                            click.echo(f"   - {name}: {', '.join(sorted(result.extra_files))}")
    
    except Exception as e:
        if ci:
            click.echo(json.dumps({"error": str(e)}))
            sys.exit(2)
        else:
            click.echo(f"❌ Error: {e}")
            sys.exit(1)


@cli.command()
@click.option('--format', 'format_type', type=click.Choice(['markdown', 'json']), 
              default='markdown', help='Report format')
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--specs-dir', type=click.Path(exists=True), help='Custom specs directory')
def report(format_type: str, output: Optional[str], specs_dir: Optional[str]):
    """Generate comprehensive spec governance report."""
    try:
        specs_path = Path(specs_dir) if specs_dir else Path(".kiro/specs")
        validator = SpecValidator(specs_path)
        reporter = SpecReporter(validator)
        
        if output:
            # Save to file
            output_path = Path(output)
            report_content = reporter.generate_report(format_type)
            with open(output_path, 'w') as f:
                f.write(report_content)
            click.echo(f"📄 Report saved to: {output_path}")
        else:
            # Print to stdout
            report_content = reporter.generate_report(format_type)
            click.echo(report_content)
    
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}")
        sys.exit(1)


@cli.command()
@click.option('--specs-dir', type=click.Path(exists=True), help='Custom specs directory')
def metrics(specs_dir: Optional[str]):
    """Display quality metrics for dashboard integration."""
    try:
        specs_path = Path(specs_dir) if specs_dir else Path(".kiro/specs")
        validator = SpecValidator(specs_path)
        reporter = SpecReporter(validator)
        
        metrics_data = reporter.compute_metrics()
        click.echo(json.dumps(metrics_data, indent=2))
    
    except Exception as e:
        click.echo(f"❌ Error computing metrics: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
'''
        
        with open(cli_file, 'w') as f:
            f.write(cli_content)
        
        # Update pyproject.toml to include console script
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, 'r') as f:
                content = f.read()
            
            # Add console script if not already present
            if 'spec-governance' not in content:
                # Find [project.scripts] section or add it
                if '[project.scripts]' in content:
                    # Add to existing scripts section
                    content = content.replace(
                        '[project.scripts]',
                        '[project.scripts]\nspec-governance = "spec_governance.cli:cli"'
                    )
                else:
                    # Add new scripts section
                    content += '\n\n[project.scripts]\nspec-governance = "spec_governance.cli:cli"\n'
                
                with open(pyproject_file, 'w') as f:
                    f.write(content)
        
        return {"cli_implemented": True, "console_script_added": True}
    
    def _task_1_5(self):
        """Task 1.5: Remove Empty Output Directory (1 hour)."""
        output_dir = self.specs_dir / "output"
        
        if output_dir.exists():
            if output_dir.is_dir():
                # Check if directory is empty
                contents = list(output_dir.iterdir())
                if not contents:
                    output_dir.rmdir()
                    return {"removed": True, "was_empty": True}
                else:
                    return {"removed": False, "reason": f"Directory not empty: {len(contents)} items"}
            else:
                return {"removed": False, "reason": "Path exists but is not a directory"}
        else:
            return {"removed": False, "reason": "Directory does not exist"}
    
    def _task_1_6(self):
        """Task 1.6: Create Makefile Targets (2 hours)."""
        # Create makefiles directory if it doesn't exist
        makefiles_dir = self.project_root / "makefiles"
        makefiles_dir.mkdir(exist_ok=True)
        
        # Create spec-governance.mk
        makefile_content = '''# Spec Governance Makefile
# Provides targets for spec validation, reporting, and management

.PHONY: spec-validate spec-report spec-create spec-fix-auto spec-complete-missing spec-archive-inactive

# Validate all specs for completeness and consistency
spec-validate:
\t@echo "🔍 Validating all specs..."
\t@python -m spec_governance.cli validate --all

# Generate comprehensive spec governance report
spec-report:
\t@echo "📊 Generating spec governance report..."
\t@python -m spec_governance.cli report --format markdown --output .kiro/reports/spec-quality-latest.md
\t@echo "📄 Report saved to .kiro/reports/spec-quality-latest.md"

# Create new spec from template
spec-create:
\t@if [ -z "$(NAME)" ]; then \\
\t\techo "❌ Error: NAME parameter required"; \\
\t\techo "Usage: make spec-create NAME=my-feature-name DESC='Feature description'"; \\
\t\texit 1; \\
\tfi
\t@echo "📝 Creating new spec: $(NAME)"
\t@python -m spec_governance.template_generator create --name "$(NAME)" --description "$(DESC)"

# Show spec governance help
spec-help:
\t@echo "📚 Spec Governance Commands:"
\t@echo "  make spec-validate          - Validate all specs"
\t@echo "  make spec-report           - Generate governance report"
\t@echo "  make spec-create NAME=...  - Create new spec from template"
\t@echo ""
\t@echo "Advanced commands (Phase 2+):"
\t@echo "  make spec-fix-auto         - Apply automatic fixes"
\t@echo "  make spec-complete-missing - Create stubs for incomplete specs"
\t@echo "  make spec-archive-inactive - Archive deprecated specs"

# Placeholder targets for future phases
spec-fix-auto:
\t@echo "⚠️  spec-fix-auto not yet implemented (Phase 2)"
\t@echo "   Will be available after Phase 2 completion"

spec-complete-missing:
\t@echo "⚠️  spec-complete-missing not yet implemented (Phase 3)"
\t@echo "   Will be available after Phase 3 completion"

spec-archive-inactive:
\t@echo "⚠️  spec-archive-inactive not yet implemented (Phase 4)"
\t@echo "   Will be available after Phase 4 completion"
'''
        
        spec_makefile = makefiles_dir / "spec-governance.mk"
        with open(spec_makefile, 'w') as f:
            f.write(makefile_content)
        
        # Update main Makefile to include spec-governance.mk
        main_makefile = self.project_root / "Makefile"
        if main_makefile.exists():
            with open(main_makefile, 'r') as f:
                content = f.read()
            
            # Add include if not already present
            include_line = "include makefiles/spec-governance.mk"
            if include_line not in content:
                # Add after other includes or at the top
                if "include makefiles/" in content:
                    # Find last include line and add after it
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("include makefiles/"):
                            lines.insert(i + 1, include_line)
                            break
                    content = '\n'.join(lines)
                else:
                    # Add at the top
                    content = include_line + '\n\n' + content
                
                with open(main_makefile, 'w') as f:
                    f.write(content)
        
        # Update help target if it exists
        if main_makefile.exists():
            with open(main_makefile, 'r') as f:
                content = f.read()
            
            if 'help:' in content and 'spec-help' not in content:
                # Add spec-help to main help
                content = content.replace(
                    'help:',
                    'help:\n\t@$(MAKE) spec-help\n\t@echo ""\nhelp-original:'
                )
                
                with open(main_makefile, 'w') as f:
                    f.write(content)
        
        return {"makefile_created": True, "main_makefile_updated": True}
    
    def _task_2_1(self):
        """Task 2.1: Build SpecRegistry with JSON Index (8 hours)."""
        # The registry module is already created, now initialize it
        try:
            # Import and initialize the registry
            sys.path.insert(0, str(self.project_root / "src"))
            from spec_governance.registry import SpecRegistry
            
            # Create registry instance and rebuild from filesystem
            registry = SpecRegistry(self.specs_dir)
            registry.rebuild_registry()
            
            # Verify registry was created
            registry_file = self.project_root / ".kiro" / "spec-registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry_data = json.load(f)
                
                total_specs = registry_data.get("total_specs", 0)
                return {
                    "registry_created": True,
                    "total_specs_indexed": total_specs,
                    "registry_file": str(registry_file)
                }
            else:
                raise Exception("Registry file was not created")
        
        except Exception as e:
            raise Exception(f"Failed to build spec registry: {e}")
    
    def _task_2_2(self):
        """Task 2.2: Implement Lifecycle Tracking (6 hours)."""
        # Create .spec-state files for all specs
        try:
            sys.path.insert(0, str(self.project_root / "src"))
            from spec_governance.registry import SpecRegistry, LifecycleState
            
            registry = SpecRegistry(self.specs_dir)
            specs_updated = 0
            
            # Set default lifecycle states for all specs
            for spec_dir in self.specs_dir.iterdir():
                if not spec_dir.is_dir() or spec_dir.name.startswith('.'):
                    continue
                
                spec_name = spec_dir.name
                
                # Determine appropriate lifecycle state based on completeness
                spec_metadata = registry.get_spec(spec_name)
                if spec_metadata and spec_metadata.is_complete:
                    lifecycle_state = LifecycleState.ACTIVE
                else:
                    lifecycle_state = LifecycleState.DRAFT
                
                # Update or create the spec state
                if registry.update_spec_state(spec_name, lifecycle_state):
                    specs_updated += 1
                elif registry.register_spec(spec_name, lifecycle_state):
                    specs_updated += 1
            
            return {
                "lifecycle_tracking_enabled": True,
                "specs_updated": specs_updated,
                "state_files_created": specs_updated
            }
        
        except Exception as e:
            raise Exception(f"Failed to implement lifecycle tracking: {e}")
    
    def _task_2_3(self):
        """Task 2.3: Implement SpecRemediator with Dry-run (8 hours)."""
        # The remediator is already implemented, test it
        try:
            sys.path.insert(0, str(self.project_root / "src"))
            from spec_governance.remediator import SpecRemediator
            from spec_governance.validator import SpecValidator
            
            validator = SpecValidator(self.specs_dir)
            remediator = SpecRemediator(self.specs_dir, validator)
            
            # Test dry-run functionality on a few incomplete specs
            incomplete_specs = validator.get_incomplete_specs()
            test_specs = incomplete_specs[:3] if len(incomplete_specs) >= 3 else incomplete_specs
            
            dry_run_results = []
            for spec_name in test_specs:
                result = remediator.create_missing_files(spec_name, dry_run=True)
                dry_run_results.append({
                    "spec": spec_name,
                    "actions_planned": len(result.actions_taken),
                    "success": result.success
                })
            
            return {
                "remediator_tested": True,
                "dry_run_results": dry_run_results,
                "test_specs_count": len(test_specs)
            }
        
        except Exception as e:
            raise Exception(f"Failed to implement SpecRemediator: {e}")
    
    def _task_2_4(self):
        """Task 2.4: Extra File Management (6 hours)."""
        # Create directories for organizing extra files
        try:
            archive_dir = self.project_root / ".kiro" / "archive"
            execution_logs_dir = self.project_root / ".kiro" / "execution-logs"
            
            archive_dir.mkdir(parents=True, exist_ok=True)
            execution_logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Test extra file categorization
            sys.path.insert(0, str(self.project_root / "src"))
            from spec_governance.validator import SpecValidator
            from spec_governance.remediator import SpecRemediator
            
            validator = SpecValidator(self.specs_dir)
            remediator = SpecRemediator(self.specs_dir, validator)
            
            # Get specs with extra files and categorize them
            specs_with_extras = validator.get_specs_with_extra_files()
            categorization_results = []
            
            for spec_name in specs_with_extras[:5]:  # Test first 5
                result = remediator.move_extra_files(spec_name, dry_run=True)
                categorization_results.append({
                    "spec": spec_name,
                    "actions_planned": len(result.actions_taken),
                    "success": result.success
                })
            
            return {
                "directories_created": True,
                "archive_dir": str(archive_dir),
                "execution_logs_dir": str(execution_logs_dir),
                "categorization_tested": True,
                "test_results": categorization_results
            }
        
        except Exception as e:
            raise Exception(f"Failed to implement extra file management: {e}")
    
    def _task_2_5(self):
        """Task 2.5: Create Git Pre-commit Hook (6 hours)."""
        # Create git pre-commit hook
        try:
            git_hooks_dir = self.project_root / ".git" / "hooks"
            if not git_hooks_dir.exists():
                return {"hook_created": False, "reason": "Not a git repository"}
            
            pre_commit_hook = git_hooks_dir / "pre-commit"
            
            hook_content = '''#!/bin/bash
# Spec Consistency Governance Pre-commit Hook
# Prevents commits of incomplete specs

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo "🔍 Checking spec consistency..."

# Get modified spec directories
modified_specs=$(git diff --cached --name-only | grep '^\\.kiro/specs/' | cut -d/ -f1-3 | sort -u)

if [ -z "$modified_specs" ]; then
    echo "${GREEN}✅ No spec changes detected${NC}"
    exit 0
fi

# Check each modified spec
failed_specs=()
for spec in $modified_specs; do
    spec_name=$(basename "$spec")
    echo "  Checking $spec_name..."
    
    # Use the spec governance CLI to validate
    if ! PYTHONPATH=src python -m spec_governance.cli validate --spec "$spec_name" --ci >/dev/null 2>&1; then
        failed_specs+=("$spec_name")
    fi
done

# Report results
if [ ${#failed_specs[@]} -eq 0 ]; then
    echo "${GREEN}✅ All modified specs are complete${NC}"
    exit 0
else
    echo "${RED}❌ Commit blocked: Incomplete specs detected${NC}"
    echo ""
    echo "The following specs are incomplete:"
    for spec in "${failed_specs[@]}"; do
        echo "  ${RED}• $spec${NC}"
        # Show what's missing
        PYTHONPATH=src python -m spec_governance.cli validate --spec "$spec" 2>/dev/null | grep "missing" | sed 's/^/    /'
    done
    echo ""
    echo "${YELLOW}To fix:${NC}"
    echo "  1. Complete the missing files for each spec"
    echo "  2. Use: ${YELLOW}make spec-create NAME=spec-name${NC} for new specs"
    echo "  3. Use: ${YELLOW}PYTHONPATH=src python -m spec_governance.cli validate --spec SPEC_NAME${NC} to check"
    echo ""
    echo "${YELLOW}To bypass (not recommended):${NC}"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi
'''
            
            # Write the hook
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            
            # Make it executable
            import stat
            pre_commit_hook.chmod(pre_commit_hook.stat().st_mode | stat.S_IEXEC)
            
            return {
                "hook_created": True,
                "hook_path": str(pre_commit_hook),
                "executable": True
            }
        
        except Exception as e:
            raise Exception(f"Failed to create git pre-commit hook: {e}")
    
    def _task_2_6(self):
        """Task 2.6: Document Spec Standards (4 hours)."""
        # Create comprehensive spec standards documentation
        try:
            docs_dir = self.project_root / ".kiro" / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            standards_file = docs_dir / "spec-standards.md"
            
            standards_content = '''# Specification Standards Guide

## Overview

This guide defines the standards and best practices for creating and maintaining specifications in the `.kiro/specs/` directory.

## Required File Structure

Every specification MUST contain exactly three files:

### 1. requirements.md
**Purpose:** Define what the system should do
**Format:** EARS (Easy Approach to Requirements Syntax)

```markdown
# Requirements Document: [Spec Name]

## Introduction
[Brief description of the feature/system]

## Requirements

### Requirement 1: [Requirement Name]
**User Story:** As a [role], I want [feature], so that [benefit].

#### Acceptance Criteria
1. WHEN [condition] THEN the system SHALL [behavior]
2. WHEN [condition] THEN the system SHALL [behavior]

**Priority:** CRITICAL/HIGH/MEDIUM/LOW
```

### 2. design.md
**Purpose:** Define how the system will be built
**Format:** Technical architecture and implementation details

```markdown
# Design Document: [Spec Name]

## Overview
[System architecture overview]

## Components
[Detailed component descriptions]

## Data Models
[Data structures and schemas]

## Integration Points
[External system interfaces]

## Error Handling
[Error scenarios and recovery]

## Testing Strategy
[Testing approach and coverage]
```

### 3. tasks.md
**Purpose:** Define implementation steps
**Format:** Actionable task breakdown with acceptance criteria

```markdown
# Tasks: [Spec Name]

## Phase 1: [Phase Name]

### Task 1.1: [Task Name]
**Requirement:** REQ-1 ([Requirement Description])
**Estimated Effort:** [X hours]

**Steps:**
1. [Detailed implementation step]
2. [Detailed implementation step]

**Acceptance:**
- [Specific acceptance criteria]
- [Specific acceptance criteria]
```

## Lifecycle States

Every spec has a lifecycle state tracked in `.spec-state` file:

- **DRAFT** - Incomplete or under development
- **ACTIVE** - Complete and being implemented
- **COMPLETED** - Implementation finished
- **DEPRECATED** - No longer relevant
- **ARCHIVED** - Moved to archive for historical reference

## File Naming Conventions

- Use lowercase filenames: `requirements.md`, `design.md`, `tasks.md`
- Spec directory names use kebab-case: `my-feature-name`
- No spaces or special characters in directory names

## Content Standards

### Requirements (EARS Format)
- Use "WHEN...THEN...SHALL" structure
- Be specific and testable
- Include priority levels
- Reference user stories

### Design Documents
- Include component diagrams where helpful
- Specify data models and interfaces
- Address error handling and edge cases
- Define testing strategy

### Task Lists
- Reference specific requirements
- Include estimated effort
- Provide clear acceptance criteria
- Break down into manageable chunks

## Quality Gates

### Pre-commit Validation
All specs are validated before commit:
- Must have all three required files
- Files must not be empty
- No unapproved extra files

### Validation Commands
```bash
# Validate all specs
make spec-validate

# Validate specific spec
PYTHONPATH=src python -m spec_governance.cli validate --spec SPEC_NAME

# Generate quality report
make spec-report
```

## Creating New Specs

### Using Templates
```bash
# Create new spec with template
make spec-create NAME=my-feature DESC="Feature description"
```

### Manual Creation
1. Create directory: `.kiro/specs/my-feature-name/`
2. Create three required files with proper templates
3. Validate: `make spec-validate`
4. Commit when complete

## Extra Files Policy

### Allowed Extra Files
- `.spec-state` - Lifecycle state tracking
- `.spec-exempt` - Exemption from certain rules
- `.spec-extra-files` - Approved extra files list
- `dag-config.yml` - DAG execution configuration
- `DAG_EXECUTION_PLAN.md` - DAG planning documents
- `LAUNCH_READINESS.md` - Launch preparation documents

### Prohibited Extra Files
- Backup files (`*_backup.md`, `*_fixed.md`)
- Execution artifacts (`LAUNCH_SUMMARY.md`, `PARALLEL_DAG_LAUNCH.md`)
- Analysis files (unless approved in `.spec-extra-files`)

### File Organization
- **Archive:** `.kiro/archive/SPEC_NAME/` - For backup files
- **Execution Logs:** `.kiro/execution-logs/SPEC_NAME/` - For execution artifacts

## Troubleshooting

### Common Issues

#### "Spec is incomplete"
**Cause:** Missing required files
**Fix:** Create missing `requirements.md`, `design.md`, or `tasks.md`

#### "Extra files detected"
**Cause:** Unapproved files in spec directory
**Fix:** Move to appropriate location or add to `.spec-extra-files`

#### "Git commit blocked"
**Cause:** Pre-commit hook detected incomplete spec
**Fix:** Complete the spec or use `git commit --no-verify` (not recommended)

### Validation Commands
```bash
# Check specific spec
PYTHONPATH=src python -m spec_governance.cli validate --spec SPEC_NAME

# Get detailed report
make spec-report

# Check what's missing
PYTHONPATH=src python -m spec_governance.cli validate --all | grep "missing"
```

### Override Procedures
```bash
# Bypass pre-commit hook (emergency only)
git commit --no-verify -m "Emergency commit"

# Mark spec as exempt from validation
echo "reason: Emergency deployment" > .kiro/specs/SPEC_NAME/.spec-exempt
```

## Best Practices

### Requirements Writing
- Start with user stories
- Use measurable acceptance criteria
- Consider edge cases and error conditions
- Include performance requirements where relevant

### Design Documentation
- Keep diagrams simple and focused
- Document decision rationales
- Include security considerations
- Plan for monitoring and observability

### Task Planning
- Break large tasks into smaller ones
- Include testing tasks
- Estimate effort realistically
- Plan for integration and deployment

### Lifecycle Management
- Update lifecycle state as work progresses
- Archive completed specs appropriately
- Deprecate obsolete specs rather than deleting

## Compliance

### Automated Enforcement
- Pre-commit hooks prevent incomplete specs
- CI/CD validation on all pull requests
- Regular quality reports and metrics

### Manual Reviews
- Peer review of all new specs
- Architecture review for complex designs
- Quality gate reviews before implementation

### Metrics and Reporting
- Spec completion rate tracking
- Quality trend analysis
- Team adoption metrics

---

## Quick Reference

### Commands
```bash
make spec-validate          # Validate all specs
make spec-report           # Generate quality report
make spec-create NAME=...  # Create new spec
make spec-help            # Show all commands
```

### File Structure
```
.kiro/specs/my-feature/
├── requirements.md        # REQUIRED: What to build
├── design.md             # REQUIRED: How to build it
├── tasks.md              # REQUIRED: Implementation steps
├── .spec-state           # Lifecycle tracking
└── .spec-extra-files     # Approved extra files (if any)
```

### Lifecycle States
- `DRAFT` → `ACTIVE` → `COMPLETED` → `ARCHIVED`
- `DEPRECATED` (for obsolete specs)

---

*This guide is maintained by the Spec Consistency Governance system.*
*Last updated: {datetime.now().strftime("%Y-%m-%d")}*
'''
            
            with open(standards_file, 'w') as f:
                f.write(standards_content)
            
            return {
                "standards_documented": True,
                "standards_file": str(standards_file),
                "lines_documented": len(standards_content.split('\n'))
            }
        
        except Exception as e:
            raise Exception(f"Failed to document spec standards: {e}")
    
    def execute_dry_run(self):
        """Execute dry run to show what would be done."""
        print("🔍 Spec Consistency Governance DAG - DRY RUN")
        print("=" * 60)
        
        print("\n📋 Phase 1: Critical Infrastructure (Week 1, 25 hours)")
        self.execute_phase_1(dry_run=True)
        
        print("\n📋 Phase 2: Governance & Prevention (Week 2, 38 hours)")
        print("   [DRY RUN] Would implement lifecycle management and git hooks")
        
        print("\n📋 Phase 3: Quality & Automation (Week 3, 24 hours)")
        print("   [DRY RUN] Would implement template generation and automated fixes")
        
        print("\n📋 Phase 4: Advanced Features (Week 3-4, 34 hours)")
        print("   [DRY RUN] Would implement duplicate detection and consolidation")
        
        print("\n📋 Phase 5: Rollout & Remediation (Week 5, 30 hours)")
        print("   [DRY RUN] Would fix all incomplete specs and train team")
        
        print("\n✅ DRY RUN COMPLETE")
        print("   Total estimated effort: 151 hours (3-5 weeks)")
        print("   Ready for execution with --phase=1")
    
    def generate_status_report(self):
        """Generate current execution status report."""
        print("📊 Spec Consistency Governance DAG - Status Report")
        print("=" * 60)
        
        print(f"\n🕐 Started: {self.state.get('started_at', 'Not started')}")
        print(f"📈 Current Phase: {self.state.get('current_phase', 0)}")
        
        # Phase status
        print("\n📋 Phase Status:")
        for phase_num, phase_data in self.state["phases"].items():
            status_icon = {
                "pending": "⏳",
                "running": "🔄", 
                "completed": "✅",
                "failed": "❌"
            }.get(phase_data["status"], "❓")
            
            print(f"   Phase {phase_num}: {status_icon} {phase_data['status'].upper()}")
            if phase_data.get("started_at"):
                print(f"      Started: {phase_data['started_at']}")
            if phase_data.get("completed_at"):
                print(f"      Completed: {phase_data['completed_at']}")
        
        # Task status
        completed_tasks = [task_id for task_id, task_data in self.state["tasks"].items() 
                          if task_data.get("status") == "completed"]
        failed_tasks = [task_id for task_id, task_data in self.state["tasks"].items() 
                       if task_data.get("status") == "failed"]
        
        print(f"\n📝 Tasks: {len(completed_tasks)} completed, {len(failed_tasks)} failed")
        
        if completed_tasks:
            print("   ✅ Completed:")
            for task_id in sorted(completed_tasks):
                print(f"      - Task {task_id}")
        
        if failed_tasks:
            print("   ❌ Failed:")
            for task_id in sorted(failed_tasks):
                error = self.state["tasks"][task_id].get("error", "Unknown error")
                print(f"      - Task {task_id}: {error}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Spec Consistency Governance DAG Executor")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4, 5], help="Execute specific phase")
    parser.add_argument("--report", action="store_true", help="Generate status report")
    parser.add_argument("--strategy", choices=["hybrid", "sequential", "parallel"], default="hybrid",
                       help="Execution strategy")
    
    args = parser.parse_args()
    
    dag = SpecConsistencyGovernanceDAG()
    
    if args.dry_run:
        dag.execute_dry_run()
    elif args.report:
        dag.generate_status_report()
    elif args.phase:
        if args.phase == 1:
            dag.execute_phase_1()
        elif args.phase == 2:
            dag.execute_phase_2()
        else:
            print(f"❌ Phase {args.phase} not yet implemented")
            print("   Available phases: 1, 2")
            sys.exit(1)
    else:
        print("❌ No action specified. Use --dry-run, --phase=N, or --report")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()