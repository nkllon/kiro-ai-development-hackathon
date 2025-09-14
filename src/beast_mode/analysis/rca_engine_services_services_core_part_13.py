
def _analyze_configuration(self, failure: Failure) -> Dict[str, Any]:
    """Analyze configuration issues"""
    config_analysis = {}
    config_files = ['.env', 'config.json', 'settings.py', 'Makefile']
    for config_file in config_files:
        config_analysis[f'{config_file}_exists'] = Path(config_file).exists()
    return config_analysis
