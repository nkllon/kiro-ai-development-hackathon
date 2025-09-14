from src.rm_ddd.core.health import ModuleHealth

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
