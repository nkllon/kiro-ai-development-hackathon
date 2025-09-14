"""
Dag Cli Core

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

@click.group()
@click.version_option(version='0.6.1-mvp-foundation-complete')
def beast_dag():
    """
    🔥 BEAST MODE DAG Orchestration CLI
    
    Systematic superiority for complex ecosystem orchestration.
    Beastmaster Bobby approved - can handle ANY specification complexity.
    """
    pass

@beast_dag.command()
@click.argument('spec_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table', help='Output format for analysis results')
@click.option('--save', '-s', type=click.Path(), help='Save analysis results to file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output with detailed analysis')
def analyze(spec_directory: str, output: str, save: Optional[str], verbose: bool):
    """
    🔍 SYSTEMATICALLY ANALYZE ecosystem with BEASTMASTER precision.
    
    Performs comprehensive dependency analysis, critical path calculation,
    and systematic quality assessment of specification ecosystem.
    
    Examples:
        beast-dag analyze .kiro/specs --output table
        beast-dag analyze /path/to/specs --output json --save analysis.json
    """
    click.echo(f'🔍 BEAST MODE ANALYSIS: {spec_directory}')
    click.echo('⚡ Systematic ecosystem consumption initiated...')
    try:
        loop = asyncio.get_event_loop()
        ecosystem_dag = loop.run_until_complete(orchestration_engine.dependency_analyzer.analyze_ecosystem_dependencies(spec_directory))
        analysis_data = {'ecosystem_id': ecosystem_dag.ecosystem_id, 'total_specifications': len(ecosystem_dag.specifications), 'total_tasks': len(ecosystem_dag.tasks), 'completion_percentage': ecosystem_dag.completion_percentage, 'estimated_remaining_effort': ecosystem_dag.estimated_remaining_effort, 'critical_paths': len(ecosystem_dag.critical_paths), 'parallel_opportunities': len(ecosystem_dag.parallel_opportunities), 'analysis_timestamp': ecosystem_dag.analysis_timestamp.isoformat()}
        if verbose:
            analysis_data.update({'specifications': [{'name': spec.spec_name, 'completion': f'{spec.completion_percentage:.1f}%', 'tasks': f'{spec.completed_tasks}/{spec.task_count}', 'layer': spec.layer} for spec in ecosystem_dag.specifications], 'critical_path_details': [{'path_id': cp.path_id, 'duration_hours': cp.total_duration, 'tasks': len(cp.task_sequence), 'risk_level': cp.risk_level.value} for cp in ecosystem_dag.critical_paths[:5]], 'critical_path_summary': f'{len(ecosystem_dag.critical_paths)} paths identified'})
        _output_results(analysis_data, output, save)
        click.echo(f'✅ ANALYSIS COMPLETE: {len(ecosystem_dag.specifications)} specs, {len(ecosystem_dag.tasks)} tasks')
        click.echo(f'📊 Completion: {ecosystem_dag.completion_percentage:.1f}%')
        click.echo(f'⚡ Parallel opportunities: {len(ecosystem_dag.parallel_opportunities)}')
    except Exception as e:
        click.echo(f'❌ ANALYSIS FAILED: {str(e)}', err=True)
        raise click.ClickException(str(e))

@beast_dag.command()
@click.argument('spec_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--timeline', '-t', type=int, default=12, help='Maximum timeline in weeks')
@click.option('--effort', '-e', type=int, default=1000, help='Maximum effort in hours')
@click.option('--strategy', type=click.Choice(['minimum', 'value', 'risk', 'balanced']), default='balanced', help='MVP route strategy')
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')
@click.option('--save', '-s', type=click.Path(), help='Save MVP route to file')
def mvp_route(spec_directory: str, timeline: int, effort: int, strategy: str, output: str, save: Optional[str]):
    """
    🎯 CALCULATE MVP route with SYSTEMATIC optimization.
    
    Calculates optimal route to MVP delivery with systematic value demonstration,
    risk assessment, and parallel execution optimization.
    
    Examples:
        beast-dag mvp-route .kiro/specs --timeline 8 --effort 800
        beast-dag mvp-route /path/to/specs --strategy minimum --output json
    """
    click.echo(f'🎯 BEAST MODE MVP CALCULATION: {spec_directory}')
    click.echo(f'⚡ Strategy: {strategy}, Timeline: {timeline}w, Effort: {effort}h')
    try:
        mvp_criteria = MVPCriteria(required_deliverables=['Functional API', 'Core Framework', 'Basic Testing'], success_metrics={'quality_score': 0.9}, maximum_timeline=timeline, maximum_effort=effort, minimum_value_demonstration=['End-to-end workflow'], quality_gates={'systematic_score': 0.9}, risk_tolerance=RiskImpact.MEDIUM)
        loop = asyncio.get_event_loop()
        orchestration_result = loop.run_until_complete(orchestration_engine.orchestrate_ecosystem_execution_with_extreme_prejudice(spec_directory, mvp_criteria, resource_constraints=None))
        mvp_data = {'route_id': orchestration_result.mvp_route.route_id, 'estimated_timeline_weeks': orchestration_result.mvp_route.estimated_timeline, 'total_effort_hours': orchestration_result.mvp_route.total_estimated_effort, 'success_probability': orchestration_result.mvp_route.success_probability, 'phases': [{'phase': phase.phase_number, 'name': phase.phase_name, 'tasks': len(phase.tasks), 'duration_weeks': phase.estimated_duration, 'objectives': phase.objectives, 'deliverables': phase.deliverables} for phase in orchestration_result.mvp_route.phases], 'risk_factors': len(orchestration_result.risk_assessment.risk_factors), 'parallel_groups': len(orchestration_result.optimized_execution.parallel_groups), 'systematic_quality_score': orchestration_result.systematic_quality_score}
        _output_results(mvp_data, output, save)
        click.echo(f'✅ MVP ROUTE CALCULATED: {orchestration_result.orchestration_id}')
        click.echo(f'📊 Timeline: {orchestration_result.mvp_route.estimated_timeline} weeks')
        click.echo(f'🎯 Success Probability: {orchestration_result.mvp_route.success_probability:.1%}')
        click.echo(f'⚡ Systematic Quality: {orchestration_result.systematic_quality_score:.3f}')
    except Exception as e:
        click.echo(f'❌ MVP CALCULATION FAILED: {str(e)}', err=True)
        raise click.ClickException(str(e))

@beast_dag.command()
@click.argument('spec_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--execute', '-x', is_flag=True, help='Execute orchestration plan immediately')
@click.option('--parallel', '-p', type=int, default=8, help='Maximum parallel tasks')
@click.option('--timeline', '-t', type=int, default=12, help='Maximum timeline in weeks')
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')
@click.option('--monitor', '-m', is_flag=True, help='Enable real-time monitoring')
def orchestrate(spec_directory: str, execute: bool, parallel: int, timeline: int, output: str, monitor: bool):
    """
    🚀 ORCHESTRATE ecosystem with BEASTMASTER systematic prejudice.
    
    Performs complete ecosystem orchestration including analysis, MVP calculation,
    parallel optimization, and optional execution with systematic monitoring.
    
    Examples:
        beast-dag orchestrate .kiro/specs --parallel 6
        beast-dag orchestrate /path/to/specs --execute --monitor
    """
    click.echo(f'🚀 BEAST MODE ORCHESTRATION: {spec_directory}')
    click.echo(f'⚡ Parallel: {parallel}, Execute: {execute}, Monitor: {monitor}')
    try:
        resource_constraints = ResourceConstraints(max_parallel_tasks=parallel, budget_hours=timeline * 40)
        mvp_criteria = MVPCriteria(required_deliverables=['Basic Functionality', 'Working Examples'], success_metrics={'quality_score': 0.9}, maximum_timeline=timeline, maximum_effort=timeline * 40, minimum_value_demonstration=['End-to-end workflow'], quality_gates={'systematic_score': 0.9}, risk_tolerance=RiskImpact.MEDIUM)
        loop = asyncio.get_event_loop()
        orchestration_result = loop.run_until_complete(orchestration_engine.orchestrate_ecosystem_execution_with_extreme_prejudice(spec_directory, mvp_criteria, resource_constraints))
        execution_result = None
        if execute:
            click.echo('🔄 EXECUTING ORCHESTRATION PLAN...')
            execution_result = loop.run_until_complete(orchestration_engine.execute_orchestration_plan_with_systematic_monitoring(orchestration_result.orchestration_id, dry_run=False))
        orchestration_data = orchestration_result.get_summary()
        if execution_result:
            orchestration_data.update({'execution_status': execution_result.status.value, 'completed_tasks': len(execution_result.completed_tasks), 'failed_tasks': len(execution_result.failed_tasks), 'execution_time_minutes': execution_result.execution_time})
        _output_results(orchestration_data, output)
        click.echo(f'✅ ORCHESTRATION COMPLETE: {orchestration_result.orchestration_id}')
        click.echo(f'📊 Quality Score: {orchestration_result.systematic_quality_score:.3f}')
        click.echo(f'🎯 MVP Timeline: {orchestration_result.mvp_route.estimated_timeline} weeks')
        click.echo(f'⚡ Parallel Groups: {len(orchestration_result.optimized_execution.parallel_groups)}')
        if execution_result:
            click.echo(f'🚀 Execution: {execution_result.status.value}')
            click.echo(f'✅ Completed: {len(execution_result.completed_tasks)} tasks')
        if orchestration_result.recommendations:
            click.echo('\n🎯 SYSTEMATIC RECOMMENDATIONS:')
            for rec in orchestration_result.recommendations[:3]:
                click.echo(f'  • {rec}')
    except Exception as e:
        click.echo(f'❌ ORCHESTRATION FAILED: {str(e)}', err=True)
        raise click.ClickException(str(e))

@beast_dag.command()
@click.argument('orchestration_id', required=False)
@click.option('--list', '-l', is_flag=True, help='List all active orchestrations')
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')
def status(orchestration_id: Optional[str], list: bool, output: str):
    """
    📊 GET systematic status of orchestration or list active orchestrations.
    
    Examples:
        beast-dag status --list
        beast-dag status beast_orchestration_20241207_143022
    """
    try:
        if list:
            orchestrations = orchestration_engine.list_active_orchestrations()
            if not orchestrations:
                click.echo('📭 No active orchestrations found')
                return
            if output == 'table':
                headers = ['ID', 'Tasks', 'Timeline', 'Quality', 'Created']
                rows = []
                for orch in orchestrations:
                    rows.append([orch['orchestration_id'][-12:], orch.get('total_tasks', 0), f"{orch.get('estimated_timeline', 0)}w", f"{orch.get('systematic_quality_score', 0):.3f}", orch['created_at'][:10]])
                click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            else:
                _output_results(orchestrations, output)
        elif orchestration_id:
            status_data = orchestration_engine.get_orchestration_status(orchestration_id)
            if 'error' in status_data:
                click.echo(f"❌ {status_data['error']}", err=True)
                return
            _output_results(status_data, output)
            click.echo(f'📊 ORCHESTRATION STATUS: {orchestration_id}')
            click.echo(f"⚡ Progress: {status_data.get('progress_percentage', 0):.1f}%")
            click.echo(f"✅ Tasks: {status_data.get('completed_tasks', 0)}/{status_data.get('total_tasks', 0)}")
            click.echo(f"🎯 Quality Score: {status_data.get('systematic_quality_score', 0):.3f}")
        else:
            click.echo('❌ Please provide orchestration ID or use --list', err=True)
    except Exception as e:
        click.echo(f'❌ STATUS CHECK FAILED: {str(e)}', err=True)
        raise click.ClickException(str(e))

@beast_dag.command()
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')
def metrics(output: str):
    """
    📈 GET systematic orchestration metrics and performance indicators.
    
    Shows overall Beast Mode DAG orchestration system performance,
    systematic quality trends, and Beastmaster efficiency metrics.
    """
    click.echo('📈 BEAST MODE METRICS: Systematic superiority indicators')
    try:
        loop = asyncio.get_event_loop()
        metrics_data = loop.run_until_complete(orchestration_engine.get_orchestration_metrics())
        _output_results(metrics_data, output)
        click.echo(f"📊 Total Orchestrations: {metrics_data['total_orchestrations']}")
        click.echo(f"⚡ Active Orchestrations: {metrics_data['active_orchestrations']}")
        click.echo(f"🎯 Average Quality Score: {metrics_data['average_systematic_quality']:.3f}")
        click.echo(f"📅 Average MVP Timeline: {metrics_data['average_mvp_timeline']:.1f} weeks")
        if metrics_data['systematic_superiority_demonstrated']:
            click.echo('🏆 SYSTEMATIC SUPERIORITY: DEMONSTRATED ✅')
        else:
            click.echo('🎯 SYSTEMATIC SUPERIORITY: Ready for demonstration')
    except Exception as e:
        click.echo(f'❌ METRICS FAILED: {str(e)}', err=True)
        raise click.ClickException(str(e))

def _output_results(data: Dict[str, Any], output_format: str, save_path: Optional[str]=None):
    """Output results in specified format."""
    if output_format == 'json':
        result = json.dumps(data, indent=2, default=str)
    elif output_format == 'yaml':
        result = yaml.dump(data, default_flow_style=False)
    elif isinstance(data, dict):
        headers = ['Property', 'Value']
        rows = [[k, str(v)] for k, v in data.items()]
        result = tabulate(rows, headers=headers, tablefmt='grid')
    else:
        result = str(data)
    if save_path:
        Path(save_path).write_text(result)
        click.echo(f'💾 Results saved to: {save_path}')
    else:
        click.echo(result)

def _get_bobby_verdict(orchestration_result: OrchestrationResult) -> str:
    """Get Bobby's systematic verdict on ecosystem consumption."""
    quality_score = orchestration_result.systematic_quality_score
    success_prob = orchestration_result.mvp_route.success_probability
    risk_count = len(orchestration_result.risk_assessment.risk_factors)
    if quality_score > 0.9 and success_prob > 0.8:
        return 'DELICIOUS - Bobby loves systematic ecosystems'
    elif quality_score > 0.8 and success_prob > 0.7:
        return 'TASTY - Bobby consumed it with systematic satisfaction'
    elif quality_score > 0.7 and success_prob > 0.6:
        return 'EDIBLE - Bobby digested it but recommends systematic improvements'
    elif quality_score > 0.6:
        return 'TOUGH - Bobby chewed through it with systematic determination'
    else:
        return 'INDIGESTIBLE - Bobby recommends systematic remediation'
