from src.rm_ddd.core.health import ModuleHealth

def _determine_failure_type(self, error_message: str) -> str:
    """Determine failure type from error message"""
    error_lower = error_message.lower()
    if 'assertionerror' in error_lower or 'assert' in error_lower:
        return 'assertion'
    elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
        return 'import'
    elif 'filenotfounderror' in error_lower:
        return 'file_not_found'
    elif 'permissionerror' in error_lower:
        return 'permission'
    elif 'timeout' in error_lower:
        return 'timeout'
    elif 'connectionerror' in error_lower or 'network' in error_lower:
        return 'network'
    elif 'memoryerror' in error_lower:
        return 'memory'
    else:
        return 'error'
