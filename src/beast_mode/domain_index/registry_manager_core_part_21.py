from src.rm_ddd.core.health import ModuleHealth

def detect_circular_dependencies(self) -> List[List[str]]:
    """Detect circular dependencies between domains"""
    return self._validator.detect_circular_dependencies(self._domains)
