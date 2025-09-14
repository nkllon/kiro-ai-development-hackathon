from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_status(self) -> Dict[str, Any]:
    """Get status of the logger manager"""
    return {'manager_running': self.is_running, 'thread_alive': self.background_thread.is_alive() if self.background_thread else False, 'logger_status': self.logger.get_health_status()}
