"""
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
        
        return "\n".join(report)
    
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
