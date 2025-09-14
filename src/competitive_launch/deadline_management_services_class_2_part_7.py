from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def calculate_critical_path(self) -> CriticalPath:
        """Calculate critical path for remaining tasks."""
        logger.info('Calculating critical path')
        try:
            incomplete_tasks = [t for t in self.tasks if t.status != TaskStatus.COMPLETED]
            if not incomplete_tasks:
                return CriticalPath([], 0.0, 0.0, [], [])
            dependency_graph = self._build_dependency_graph(incomplete_tasks)
            critical_path_tasks = self._find_critical_path(dependency_graph, incomplete_tasks)
            total_duration = sum((task.estimated_hours for task in critical_path_tasks))
            time_remaining = (self.hackathon_deadline - datetime.now()).total_seconds() / 3600
            slack_time = max(0, time_remaining - total_duration)
            risk_factors = self._identify_risk_factors(critical_path_tasks, time_remaining)
            acceleration_opportunities = self._find_acceleration_opportunities(critical_path_tasks)
            self.critical_path = CriticalPath(path_tasks=[task.task_id for task in critical_path_tasks], total_duration_hours=total_duration, slack_time_hours=slack_time, risk_factors=risk_factors, acceleration_opportunities=acceleration_opportunities)
            logger.info(f'Critical path calculated: {len(critical_path_tasks)} tasks, {total_duration:.1f} hours')
            return self.critical_path
        except Exception as e:
            logger.error(f'Failed to calculate critical path: {e}')
            return CriticalPath([], 0.0, 0.0, [str(e)], [])

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

