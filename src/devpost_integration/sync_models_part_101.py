from src.rm_ddd.core.health import ModuleHealth

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_retries': 3, 'timeout_seconds': 300, 'batch_size': 100, 'error_threshold': 0.1}
