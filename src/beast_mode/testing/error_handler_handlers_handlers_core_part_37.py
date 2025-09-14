from src.rm_ddd.core.health import ModuleHealth

def _simplify_operation_parameters(self, operation: Callable, attempt: int) -> Callable:
    """Simplify operation parameters based on retry attempt"""
    return operation
