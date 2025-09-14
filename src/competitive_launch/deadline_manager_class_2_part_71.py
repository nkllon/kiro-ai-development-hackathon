from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def calculate_critical_path(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
        Calculate critical path to hackathon deadline.
        
        Args:
            tasks: List of tasks with dependencies and estimates
            
        Returns:
            Dict containing critical path analysis
        """
    logger.info(f'Calculating critical path for {len(tasks)} tasks')
    try:
        dependency_graph = self._build_dependency_graph(tasks)
        logger.info(f'Dependency graph: {dependency_graph}')
        try:
            task_analysis = self._analyze_task_durations(tasks, dependency_graph)
            logger.info(f'Task analysis: {task_analysis}')
        except Exception as e:
            logger.error(f'Error in _analyze_task_durations: {e}')
            raise
        try:
            critical_path = self._identify_critical_path(task_analysis, dependency_graph)
        except Exception as e:
            logger.error(f'Error in _identify_critical_path: {e}')
            raise
        try:
            risk_analysis = self._calculate_deadline_risk(critical_path, task_analysis)
        except Exception as e:
            logger.error(f'Error in _calculate_deadline_risk: {e}')
            raise
        try:
            acceleration_plan = self._generate_acceleration_plan(risk_analysis, critical_path)
        except Exception as e:
            logger.error(f'Error in _generate_acceleration_plan: {e}')
            raise
        self.critical_path_tasks = critical_path
        result = {'critical_path': critical_path, 'total_duration_days': sum((task['duration_days'] for task in critical_path)), 'days_remaining': self._calculate_days_remaining(), 'risk_level': risk_analysis['risk_level'], 'acceleration_needed': risk_analysis['acceleration_required'], 'acceleration_plan': acceleration_plan, 'scope_reduction_options': self._identify_scope_reduction_options(tasks, critical_path)}
        logger.info(f"Critical path calculated: {result['total_duration_days']} days, {result['risk_level']} risk")
        return result
    except Exception as e:
        logger.error(f'Critical path calculation failed: {e}')
        return {'critical_path': [], 'error': str(e)}
