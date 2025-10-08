"""
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
