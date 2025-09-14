from src.rm_ddd.core.health import ModuleHealth

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