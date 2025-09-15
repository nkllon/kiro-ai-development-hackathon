"""
Command-line interface for RM-DDD SDK.

Provides CLI commands for working with the RM-DDD framework including
code generation, validation, and ecosystem information.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from . import __version__, get_ecosystem_info, quick_start_example
from .core.registry import get_global_registry
from .core.compliance import get_global_compliance_orchestrator

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose: bool):
    """RM-DDD SDK: Systematic Domain-Driven Development Framework"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@main.command()
def info():
    """Display ecosystem information"""
    ecosystem_info = get_ecosystem_info()

    console.print(
        Panel.fit(
            f"[bold blue]RM-DDD SDK v{ecosystem_info['rm_ddd_version']}[/bold blue]\n"
            f"[italic]{ecosystem_info['philosophy']}[/italic]",
            title="Beast Mode Ecosystem",
        )
    )

    # Create components table
    table = Table(title="Ecosystem Components")
    table.add_column("Component", style="cyan")
    table.add_column("Description", style="white")

    component_descriptions = {
        "Beast Mode Framework": "Systematic development methodology with PDCA cycles",
        "Ghostbusters AI Agents": "Multi-agent system for intelligent code analysis",
        "Spec-to-Code Engine": "Automated transformation from specs to code",
        "Intelligent Quality System": "AI-powered validation with >90% coverage",
        "RM Registry": "Component discovery and health monitoring",
    }

    for component in ecosystem_info["ecosystem_components"]:
        description = component_descriptions.get(component, "Core ecosystem component")
        table.add_row(component, description)

    console.print(table)

    console.print(f"\n[bold]Documentation:[/bold] {ecosystem_info['documentation']}")
    console.print(f"[bold]Ecosystem Guide:[/bold] {ecosystem_info['ecosystem_docs']}")


@main.command()
def quickstart():
    """Display quick start example"""
    example_code = quick_start_example()

    console.print(
        Panel(
            "This example shows how to create a domain entity with systematic validation:",
            title="Quick Start Example",
        )
    )

    syntax = Syntax(example_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    console.print("\n[bold green]Next Steps:[/bold green]")
    console.print("1. Install: [cyan]pip install rm-ddd[/cyan]")
    console.print("2. Copy the example above to get started")
    console.print("3. Read the docs: [cyan]https://rm-ddd.readthedocs.io/[/cyan]")


@main.command()
@click.option("--output", "-o", type=click.Path(), help="Output file for the report")
async def health():
    """Check system health status"""
    console.print("[bold]Checking system health...[/bold]")

    registry = get_global_registry()
    health_status = await registry.get_system_health()

    # Create health status panel
    status_color = (
        "green"
        if health_status["overall_status"] == "healthy"
        else "yellow" if health_status["overall_status"] == "degraded" else "red"
    )

    console.print(
        Panel(
            f"[bold {status_color}]{health_status['overall_status'].upper()}[/bold {status_color}]\n"
            f"Health: {health_status['health_percentage']:.1f}%\n"
            f"Modules: {health_status['healthy_modules']}/{health_status['total_modules']} healthy\n"
            f"Capabilities: {health_status['total_capabilities']} available",
            title="System Health Status",
        )
    )

    # Create modules table
    if health_status["total_modules"] > 0:
        modules = registry.get_all_modules()

        table = Table(title="Registered Modules")
        table.add_column("Module ID", style="cyan")
        table.add_column("Type", style="white")
        table.add_column("Status", style="white")
        table.add_column("Uptime", style="white")

        for module in modules:
            status_style = "green" if module.is_healthy else "red"
            uptime = str(module.uptime).split(".")[0]  # Remove microseconds

            table.add_row(
                module.module_id,
                module.module.__class__.__name__,
                f"[{status_style}]{'Healthy' if module.is_healthy else 'Unhealthy'}[/{status_style}]",
                uptime,
            )

        console.print(table)

    # Save to file if requested
    if output:
        output_path = Path(output)
        with open(output_path, "w") as f:
            json.dump(health_status, f, indent=2, default=str)
        console.print(f"\n[green]Health report saved to: {output_path}[/green]")


@main.command()
@click.option("--output", "-o", type=click.Path(), help="Output file for the report")
async def compliance():
    """Check compliance status"""
    console.print("[bold]Checking compliance status...[/bold]")

    orchestrator = get_global_compliance_orchestrator()
    compliance_reports = await orchestrator.validate_system()

    if not compliance_reports:
        console.print("[yellow]No modules registered for compliance checking[/yellow]")
        return

    # Create compliance summary table
    table = Table(title="Compliance Status")
    table.add_column("Module ID", style="cyan")
    table.add_column("Score", style="white")
    table.add_column("Violations", style="red")
    table.add_column("Warnings", style="yellow")
    table.add_column("Status", style="white")

    total_score = 0
    total_violations = 0
    total_warnings = 0

    for module_id, report in compliance_reports.items():
        status_style = "green" if report.is_compliant else "red"
        status_text = "Compliant" if report.is_compliant else "Non-Compliant"

        table.add_row(
            module_id,
            f"{report.score:.1f}%",
            str(len(report.violations)),
            str(len(report.warnings)),
            f"[{status_style}]{status_text}[/{status_style}]",
        )

        total_score += report.score
        total_violations += len(report.violations)
        total_warnings += len(report.warnings)

    console.print(table)

    # Summary
    avg_score = total_score / len(compliance_reports) if compliance_reports else 0
    summary_color = (
        "green" if avg_score >= 90 else "yellow" if avg_score >= 70 else "red"
    )

    console.print(
        Panel(
            f"[bold {summary_color}]Average Score: {avg_score:.1f}%[/bold {summary_color}]\n"
            f"Total Violations: {total_violations}\n"
            f"Total Warnings: {total_warnings}\n"
            f"Modules Checked: {len(compliance_reports)}",
            title="Compliance Summary",
        )
    )

    # Save to file if requested
    if output:
        output_path = Path(output)
        report_data = {
            module_id: {
                "score": report.score,
                "violations": report.violations,
                "warnings": report.warnings,
                "is_compliant": report.is_compliant,
                "timestamp": report.timestamp.isoformat(),
            }
            for module_id, report in compliance_reports.items()
        }

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
        console.print(f"\n[green]Compliance report saved to: {output_path}[/green]")


@main.command()
@click.argument("entity_name")
@click.argument("domain_context")
@click.option(
    "--output-dir", "-o", type=click.Path(), default=".", help="Output directory"
)
def generate_entity(entity_name: str, domain_context: str, output_dir: str):
    """Generate a domain entity class"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate entity code
    entity_code = f'''"""
{entity_name} domain entity.

Generated by RM-DDD SDK.
"""

from typing import Any, Dict, List
from rm_ddd import Entity, DomainBoundaries, ValidationResult
from rm_ddd.decorators import domain_entity


@domain_entity("{domain_context}")
class {entity_name}(Entity[str]):
    """
    {entity_name} domain entity.
    
    TODO: Add entity description and business rules.
    """
    
    def __init__(self, entity_id: str):
        super().__init__(entity_id, "{domain_context}")
        # TODO: Add entity attributes
    
    def get_domain_boundaries(self) -> DomainBoundaries:
        """Define {entity_name} domain boundaries."""
        return DomainBoundaries(
            context="{domain_context}",
            invariants=[
                # TODO: Add domain invariants
                "entity_id_not_empty"
            ],
            ubiquitous_language={{
                # TODO: Add ubiquitous language mappings
            }}
        )
    
    def validate_domain_invariants(self) -> ValidationResult:
        """Validate {entity_name} domain invariants."""
        result = ValidationResult(is_valid=True)
        
        # Basic validation
        if not self.id or not str(self.id).strip():
            result.add_error("Entity ID cannot be empty")
        
        # TODO: Add specific domain invariant validations
        
        return result
'''

    # Write to file
    file_path = output_path / f"{entity_name.lower()}.py"
    with open(file_path, "w") as f:
        f.write(entity_code)

    console.print(f"[green]Generated entity: {file_path}[/green]")
    console.print(
        f"[yellow]TODO: Customize the generated entity with your business logic[/yellow]"
    )


@main.command()
def docs():
    """Open documentation in browser"""
    import webbrowser

    docs_url = "https://rm-ddd.readthedocs.io/"
    console.print(f"Opening documentation: {docs_url}")
    webbrowser.open(docs_url)


# Async command wrapper
def async_command(f):
    """Decorator to run async commands"""

    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


# Apply async wrapper to async commands
health = async_command(health)
compliance = async_command(compliance)


if __name__ == "__main__":
    main()
