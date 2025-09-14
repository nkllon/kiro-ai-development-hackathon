from src.rm_ddd.core.health import ModuleHealth

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
