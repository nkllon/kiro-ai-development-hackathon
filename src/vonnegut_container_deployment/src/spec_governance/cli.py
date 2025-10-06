"""
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
                    click.echo("\n❌ Incomplete specs:")
                    for name, result in report.validation_results.items():
                        if not result.is_complete:
                            missing = [i.description.split(": ")[1] for i in result.issues 
                                     if i.issue_type == "missing_file"]
                            click.echo(f"   - {name}: missing {', '.join(missing)}")
                
                if report.specs_with_extra_files > 0:
                    click.echo("\n⚠️  Specs with extra files:")
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
