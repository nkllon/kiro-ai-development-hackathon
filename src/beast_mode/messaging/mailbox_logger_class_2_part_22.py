from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class GetstatusClass:
    """Auto-generated class for functions."""

    def get_status(self) -> Dict[str, Any]:
    """Get status of the logger manager"""
    return {'manager_running': self.is_running, 'thread_alive': self.background_thread.is_alive() if self.background_thread else False, 'logger_status': self.logger.get_health_status()}
