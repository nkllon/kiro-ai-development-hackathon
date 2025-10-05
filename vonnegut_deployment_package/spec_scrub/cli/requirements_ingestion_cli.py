#!/usr/bin/env python3
"""
Requirements Ingestion CLI

Command-line tool for ingesting unstructured requirements from outside the Fort
and transforming them into EARS-compliant format.

Usage:
    python -m src.spec_scrub.cli.requirements_ingestion_cli --help
"""

import click
import json
from pathlib import Path
from typing import List

from src.spec_scrub.ingestion.unstructured_requirements_ingester import (
    UnstructuredRequirementsIngester,
    RequirementSource,
    EARSRequirement
)


@click.group()
def cli():
    """Requirements Ingestion CLI - Transform unstructured requirements into EARS format."""
    pass


@cli.command()
@click.argument('text')
@click.option('--source', '-s', 
              type=click.Choice([s.value for s in RequirementSource]), 
              default='email',
              help='Source type of the requirements')
@click.option('--stakeholder', '-st', default='unknown', help='Who provided the requirements')
@click.option('--context', '-c', default='', help='Additional context about the requirements')
@click.option('--output', '-o', type=click.Path(), help='Output file for EARS requirements (JSON)')
def ingest_text(text: str, source: str, stakeholder: str, context: str, output: str):
    """Ingest requirements from text and convert to EARS format."""
    click.echo(f"🔍 Ingesting requirements from {source}...")
    
    ingester = UnstructuredRequirementsIngester()
    source_enum = RequirementSource(source)
    
    # Ingest unstructured requirements
    unstructured_reqs = ingester.ingest_from_text(text, source_enum, context, stakeholder)
    click.echo(f"📝 Found {len(unstructured_reqs)} potential requirements")
    
    # Transform to EARS format
    ears_reqs = ingester.batch_transform(unstructured_reqs)
    click.echo(f"✅ Transformed {len(ears_reqs)} requirements to EARS format")
    
    # Display results
    _display_ears_requirements(ears_reqs)
    
    # Save to file if requested
    if output:
        _save_ears_requirements(ears_reqs, Path(output))
        click.echo(f"💾 Saved to {output}")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--source', '-s', 
              type=click.Choice([s.value for s in RequirementSource]), 
              default='legacy_spec',
              help='Source type of the requirements')
@click.option('--output', '-o', type=click.Path(), help='Output file for EARS requirements (JSON)')
def ingest_file(file_path: str, source: str, output: str):
    """Ingest requirements from a file and convert to EARS format."""
    file_path = Path(file_path)
    click.echo(f"📁 Ingesting requirements from {file_path.name}...")
    
    ingester = UnstructuredRequirementsIngester()
    source_enum = RequirementSource(source)
    
    # Ingest from file
    unstructured_reqs = ingester.ingest_from_file(file_path, source_enum)
    click.echo(f"📝 Found {len(unstructured_reqs)} potential requirements")
    
    # Transform to EARS format
    ears_reqs = ingester.batch_transform(unstructured_reqs)
    click.echo(f"✅ Transformed {len(ears_reqs)} requirements to EARS format")
    
    # Display results
    _display_ears_requirements(ears_reqs)
    
    # Save to file if requested
    if output:
        _save_ears_requirements(ears_reqs, Path(output))
        click.echo(f"💾 Saved to {output}")


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for EARS requirements (JSON)')
def demo(output: str):
    """Run a demonstration of requirements ingestion with sample data."""
    click.echo("🎯 Running Requirements Ingestion Demo")
    click.echo("=" * 50)
    
    ingester = UnstructuredRequirementsIngester()
    
    # Sample unstructured requirements from different sources
    samples = [
        {
            'text': """
            Hi team, we need the login system to be more secure. Users must be able to 
            authenticate with two-factor authentication. This is critical for compliance.
            Also, the system should remember user preferences.
            """,
            'source': RequirementSource.EMAIL,
            'stakeholder': 'Product Manager',
            'context': 'Security Enhancement Request'
        },
        {
            'text': """
            PROJ-456: Implement dashboard performance improvements
            Priority: High
            
            As a user, I want the dashboard to load quickly so that I can be productive.
            
            Acceptance Criteria:
            - Dashboard must load within 2 seconds
            - Charts should render smoothly
            - Data should be cached for offline viewing
            """,
            'source': RequirementSource.JIRA,
            'stakeholder': 'Development Team',
            'context': 'Performance Sprint'
        },
        {
            'text': """
            Meeting Notes - Mobile App Planning
            
            Key decisions:
            1. App must support offline mode for core features
            2. Sync should happen automatically when online
            3. UI must be accessible for users with disabilities
            4. Performance target: app starts in under 3 seconds
            """,
            'source': RequirementSource.MEETING_NOTES,
            'stakeholder': 'Product Team',
            'context': 'Mobile Strategy Meeting'
        }
    ]
    
    all_ears_reqs = []
    
    for i, sample in enumerate(samples, 1):
        click.echo(f"\n📋 Sample {i}: {sample['source'].value.title()} from {sample['stakeholder']}")
        click.echo("-" * 40)
        
        # Ingest and transform
        unstructured_reqs = ingester.ingest_from_text(
            sample['text'], 
            sample['source'], 
            sample['context'], 
            sample['stakeholder']
        )
        
        ears_reqs = ingester.batch_transform(unstructured_reqs)
        all_ears_reqs.extend(ears_reqs)
        
        click.echo(f"Found {len(unstructured_reqs)} requirements, transformed {len(ears_reqs)} to EARS")
        
        # Show first requirement as example
        if ears_reqs:
            req = ears_reqs[0]
            click.echo(f"\n📌 Example EARS Requirement:")
            click.echo(f"   ID: {req.requirement_id}")
            click.echo(f"   User Story: {req.user_story}")
            click.echo(f"   Priority: {req.priority} ({_priority_name(req.priority)})")
            click.echo(f"   Category: {req.category}")
            click.echo(f"   Confidence: {req.confidence_score:.2f}")
            click.echo(f"   Acceptance Criteria:")
            for criteria in req.acceptance_criteria:
                click.echo(f"     - {criteria}")
    
    # Summary
    click.echo(f"\n🎉 Demo Complete!")
    click.echo(f"Total EARS Requirements Generated: {len(all_ears_reqs)}")
    
    # Category breakdown
    categories = {}
    priorities = {}
    for req in all_ears_reqs:
        categories[req.category] = categories.get(req.category, 0) + 1
        priorities[req.priority] = priorities.get(req.priority, 0) + 1
    
    click.echo(f"\nCategories: {dict(categories)}")
    click.echo(f"Priorities: {dict(priorities)}")
    
    # Save if requested
    if output:
        _save_ears_requirements(all_ears_reqs, Path(output))
        click.echo(f"💾 Demo results saved to {output}")


def _display_ears_requirements(ears_reqs: List[EARSRequirement]):
    """Display EARS requirements in a formatted way."""
    if not ears_reqs:
        click.echo("❌ No requirements generated")
        return
    
    click.echo("\n📋 EARS Requirements Generated:")
    click.echo("=" * 50)
    
    for i, req in enumerate(ears_reqs, 1):
        click.echo(f"\n{i}. {req.requirement_id}")
        click.echo(f"   User Story: {req.user_story}")
        click.echo(f"   Priority: {req.priority} ({_priority_name(req.priority)})")
        click.echo(f"   Category: {req.category}")
        click.echo(f"   Confidence: {req.confidence_score:.2f}")
        click.echo(f"   Source: {req.source_traceability}")
        click.echo(f"   Acceptance Criteria:")
        for criteria in req.acceptance_criteria:
            click.echo(f"     - {criteria}")


def _save_ears_requirements(ears_reqs: List[EARSRequirement], output_path: Path):
    """Save EARS requirements to JSON file."""
    data = []
    for req in ears_reqs:
        data.append({
            'requirement_id': req.requirement_id,
            'user_story': req.user_story,
            'acceptance_criteria': req.acceptance_criteria,
            'priority': req.priority,
            'category': req.category,
            'source_traceability': req.source_traceability,
            'confidence_score': req.confidence_score
        })
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def _priority_name(priority: int) -> str:
    """Convert priority number to name."""
    names = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low', 5: 'Lowest'}
    return names.get(priority, 'Unknown')


if __name__ == '__main__':
    cli()