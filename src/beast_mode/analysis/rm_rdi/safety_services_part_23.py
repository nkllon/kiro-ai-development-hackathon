from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _validate_initial_safety(self) -> bool:
        """Validate initial safety conditions"""
        if os.getuid() == 0:
            self.logger.error('SAFETY VIOLATION: Running as root user')
            return False
        if self.limits.max_cpu_percent > 50:
            self.logger.warning('CPU limit >50% may impact system performance')
        return True
