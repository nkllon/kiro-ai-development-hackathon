from src.rm_ddd.core.health import ModuleHealth

class StatusClass:
    """Auto-generated class for functions."""

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

    @click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'table']), default='table')