from src.rm_ddd.core.health import ModuleHealth

def get_dependencies(self) -> List[str]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get module dependencies"""
    return ['model_registry', 'reflective_module']
