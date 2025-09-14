"""
Dag Cli Validation

This module was extracted from dag_cli.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import click
from tabulate import tabulate
from ..core.orchestration_engine import OrchestrationEngine, ResourceConstraints, OrchestrationResult
from ..optimization.mvp_calculator import MVPCriteria
from ..optimization.risk_assessor import RiskImpact, SuccessProbabilityFactors
from src.rm_ddd.core.health import ModuleHealth


@beast_dag.command()
@click.argument('spec_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--complexity', type=click.Choice(['broken', 'chaotic', 'impossible']), default='chaotic', help='Test complexity level for Beastmaster Bobby consumption')
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')
class BobbytestClass:
    """Auto-generated class for functions."""

    def bobby_test(spec_directory: str, complexity: str, output: str):
    """
    🍽️ BEASTMASTER BOBBY consumption test - Can Bobby digest this ecosystem?

    Tests Beastmaster Bobby's systematic consumption tolerance against
    increasingly complex and chaotic specification ecosystems.

    Examples:
    beast-dag bobby-test .kiro/specs --complexity chaotic
    beast-dag bobby-test /path/to/nightmare/specs --complexity impossible
    """
    click.echo(f'🍽️ BEASTMASTER BOBBY TEST: {spec_directory}')
    click.echo(f'⚡ Complexity Level: {complexity.upper()}')
    click.echo("🎪 Testing Bobby's systematic consumption tolerance...")
    try:
    mvp_criteria = MVPCriteria(required_deliverables=['Basic Functionality'], success_metrics={'quality_score': 0.7}, maximum_timeline=24, maximum_effort=2000, minimum_value_demonstration=['System works'], quality_gates={'systematic_score': 0.7}, risk_tolerance=RiskImpact.HIGH)
    loop = asyncio.get_event_loop()
    orchestration_result = loop.run_until_complete(orchestration_engine.orchestrate_ecosystem_execution_with_extreme_prejudice(spec_directory, mvp_criteria))
    bobby_results = {'consumption_successful': True, 'complexity_level': complexity, 'ecosystem_size': len(orchestration_result.ecosystem_dag.specifications), 'task_count': len(orchestration_result.ecosystem_dag.tasks), 'systematic_quality_score': orchestration_result.systematic_quality_score, 'bobby_verdict': _get_bobby_verdict(orchestration_result), 'consumption_strategy': 'systematic_digestion', 'systematic_superiority': orchestration_result.systematic_quality_score > 0.8}
    _output_results(bobby_results, output)
    verdict = bobby_results['bobby_verdict']
    click.echo(f"🎪 BOBBY'S VERDICT: {verdict}")
    if bobby_results['systematic_superiority']:
    click.echo('✅ BOBBY SUCCESSFULLY CONSUMED THE ECOSYSTEM')
    click.echo('🏆 SYSTEMATIC SUPERIORITY DEMONSTRATED')
    else:
    click.echo('⚠️ BOBBY CONSUMED IT BUT RECOMMENDS SYSTEMATIC IMPROVEMENTS')
    except Exception as e:
    click.echo(f"🤮 BOBBY COULDN'T CONSUME THIS: {str(e)}")
    click.echo('💀 ECOSYSTEM DECLARED BEYOND SYSTEMATIC SALVATION')
    bobby_results = {'consumption_successful': False, 'complexity_level': complexity, 'bobby_verdict': 'BEYOND_SYSTEMATIC_SALVATION', 'recommendation': 'Complete replacement required - even Bobby has limits'}
    _output_results(bobby_results, output)

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

