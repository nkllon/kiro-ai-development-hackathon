
def distribute_tasks(self, tasks: List[Task]) -> DistributionPlan:
    """Create optimal task distribution plan using systematic analysis.
        
        Args:
            tasks: List of tasks to distribute
            
        Returns:
            DistributionPlan: Optimized distribution plan
        """
    start_time = datetime.now()
    try:
        dependency_graph = self._build_dependency_graph(tasks)
        parallel_groups = self._calculate_parallel_groups(dependency_graph)
        optimal_instances = self._calculate_optimal_instances(tasks, parallel_groups)
        plan = self._create_distribution_plan(tasks, optimal_instances, parallel_groups)
        self.distribution_history.append(plan)
        self.performance_metrics['tasks_distributed'] += len(tasks)
        self.add_health_indicator(self.create_health_indicator('task_distribution', 'healthy', f'Created distribution plan for {len(tasks)} tasks across {optimal_instances} instances', {'task_count': len(tasks), 'instance_count': optimal_instances, 'parallel_groups': len(parallel_groups), 'strategy': self.config.task_distribution_strategy.value}))
        self.update_activity()
        logger.info(f'Task distribution plan created: {len(tasks)} tasks, {optimal_instances} instances')
        return plan
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('task_distribution', 'critical', f'Failed to create distribution plan: {str(e)}', {'error': str(e), 'task_count': len(tasks)}))
        logger.error(f'Task distribution failed: {e}')
        raise
