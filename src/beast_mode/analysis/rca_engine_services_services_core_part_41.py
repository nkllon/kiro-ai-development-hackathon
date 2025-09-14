from src.rm_ddd.core.health import ModuleHealth

def _analyze_system_configuration(self, failure: Failure) -> Dict[str, Any]:
    """Analyze system configuration for infrastructure failures"""
    sys_config = {}
    try:
        sys_config['platform'] = os.uname().sysname
        sys_config['user'] = os.environ.get('USER', 'unknown')
        sys_config['home_set'] = 'HOME' in os.environ
        sys_config['path_set'] = 'PATH' in os.environ
    except Exception as e:
        sys_config['analysis_error'] = str(e)
    return sys_config
