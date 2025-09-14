from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _create_result(self, success: bool, message: str, data: Optional[Dict[str, Any]]=None, error_code: Optional[str]=None, suggestions: List[str]=None, execution_time_ms: int=0) -> GitOperationResult:
        """Create a standardized GitOperationResult"""
        status = GitOperationStatus.SUCCESS if success else GitOperationStatus.FAILURE
        return GitOperationResult(success=success, status=status, message=message, data=data, provider_used='Standard Git', execution_time_ms=execution_time_ms, error_code=error_code, suggestions=suggestions or [])

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

