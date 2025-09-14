from src.rm_ddd.core.health import ModuleHealth

def _analyze_environmental_factors(self, failure: Failure) -> Dict[str, Any]:
    """Analyze environmental factors"""
    env_analysis = {}
    env_analysis['path_set'] = 'PATH' in os.environ
    env_analysis['home_set'] = 'HOME' in os.environ
    env_analysis['working_directory'] = os.getcwd()
    return env_analysis
