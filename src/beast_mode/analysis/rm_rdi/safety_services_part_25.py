from datetime import datetime
from typing import Dict, List, Any

    def _resource_violation_callback(self, violations: List[str]) -> None:
        """Callback for resource violations"""
        self.logger.warning(f'Resource violations detected: {violations}')
        for violation in violations:
            if 'CPU usage' in violation and 'exceeds limit' in violation:
                try:
                    cpu_str = violation.split('CPU usage ')[1].split('%')[0]
                    cpu_percent = float(cpu_str)
                    if cpu_percent > self.limits.max_cpu_percent * 2:
                        self.emergency_shutdown('Severe CPU usage violation')
                        return
                except:
                    pass
            if 'Memory usage' in violation and 'exceeds limit' in violation:
                try:
                    mem_str = violation.split('Memory usage ')[1].split('MB')[0]
                    mem_mb = float(mem_str)
                    if mem_mb > self.limits.max_memory_mb * 2:
                        self.emergency_shutdown('Severe memory usage violation')
                        return
                except:
                    pass
