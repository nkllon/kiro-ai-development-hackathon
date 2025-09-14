from datetime import datetime
from typing import Dict, List, Any

    def validate_workflow_safety(self, workflow_id: str, workflow_config: Dict[str, Any]=None) -> bool:
        """Validate that a workflow is safe to execute"""
        if workflow_config is None:
            workflow_config = {}
        self.logger.info(f'Validating workflow safety: {workflow_id}')
        if self.emergency_shutdown_triggered:
            self.logger.warning(f'Workflow {workflow_id} blocked - emergency shutdown active')
            return False
        if not self.analysis_allowed:
            self.logger.warning(f'Workflow {workflow_id} blocked - analysis disabled')
            return False
        try:
            max_memory = workflow_config.get('max_memory_mb', 0)
            max_cpu = workflow_config.get('max_cpu_percent', 0)
            timeout = workflow_config.get('timeout_seconds', 300)
            if max_memory > self.limits.max_memory_mb:
                self.logger.warning(f'Workflow {workflow_id} memory requirement ({max_memory}MB) exceeds limit ({self.limits.max_memory_mb}MB)')
                return False
            if max_cpu > self.limits.max_cpu_percent:
                self.logger.warning(f'Workflow {workflow_id} CPU requirement ({max_cpu}%) exceeds limit ({self.limits.max_cpu_percent}%)')
                return False
            if timeout > self.limits.max_analysis_time_seconds:
                self.logger.warning(f'Workflow {workflow_id} timeout ({timeout}s) exceeds limit ({self.limits.max_analysis_time_seconds}s)')
                return False
            current_usage = self.resource_monitor.get_current_usage()
            if current_usage.get('cpu_percent', 0) + max_cpu > self.limits.max_cpu_percent:
                self.logger.warning(f'Workflow {workflow_id} would exceed CPU limits with current usage')
                return False
            if current_usage.get('memory_mb', 0) + max_memory > self.limits.max_memory_mb:
                self.logger.warning(f'Workflow {workflow_id} would exceed memory limits with current usage')
                return False
            workflow_type = workflow_config.get('type', 'analysis')
            if workflow_type not in ['analysis', 'validation', 'monitoring']:
                self.logger.warning(f'Workflow {workflow_id} has unsafe type: {workflow_type}')
                return False
            read_only = workflow_config.get('read_only', True)
            if not read_only:
                self.logger.warning(f'Workflow {workflow_id} is not read-only - safety violation')
                return False
            self.logger.info(f'Workflow {workflow_id} passed safety validation')
            return True
        except Exception as e:
            self.logger.error(f'Workflow safety validation failed for {workflow_id}: {e}')
            return False
