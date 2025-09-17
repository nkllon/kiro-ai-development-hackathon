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

