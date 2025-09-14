from src.rm_ddd.core.health import ModuleHealth

def get_validation_stats(self) -> Dict[str, Any]:
    """Get validation statistics"""
    return self._validator.get_validation_stats()
