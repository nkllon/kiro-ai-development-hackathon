from src.rm_ddd.core.health import ModuleHealth

def _get_infrastructure_subcategory(self, failure: Failure) -> str:
    """Get infrastructure failure subcategory"""
    if 'PermissionError' in failure.error_message:
        return 'permission_error'
    elif 'ConnectionError' in failure.error_message:
        return 'network_error'
    elif 'resource' in failure.error_message.lower():
        return 'resource_error'
    else:
        return 'general_infrastructure_error'
