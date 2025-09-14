from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _create_result(self, success: bool, message: str, data: Optional[Dict[str, Any]]=None, error_code: Optional[str]=None, suggestions: List[str]=None, execution_time_ms: int=0) -> GitOperationResult:
    """Create a standardized GitOperationResult"""
    status = GitOperationStatus.SUCCESS if success else GitOperationStatus.FAILURE
    return GitOperationResult(success=success, status=status, message=message, data=data, provider_used='Standard Git', execution_time_ms=execution_time_ms, error_code=error_code, suggestions=suggestions or [])
