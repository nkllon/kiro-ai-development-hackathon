
def _analyze_infrastructure_environment(self, failure: Failure) -> Dict[str, Any]:
    """Analyze infrastructure environment factors"""
    infra_env = {}
    try:
        import shutil
from src.rm_ddd.core.health import ModuleHealth

        total, used, free = shutil.disk_usage('.')
        infra_env['disk_space_gb'] = free // 1024 ** 3
        infra_env['disk_usage_percent'] = used / total * 100
        infra_env['memory_info_available'] = True
    except Exception as e:
        infra_env['analysis_error'] = str(e)
    return infra_env
