from src.rm_ddd.core.health import ModuleHealth

def launch_swarm(self, tasks: List[Task]) -> SwarmState:
    """Launch distributed Beast Mode swarm with systematic approach.
        
        Args:
            tasks: List of tasks to be distributed across the swarm
            
        Returns:
            SwarmState: Current state of the launched swarm
            
        Raises:
            ValueError: If tasks list is empty or configuration is invalid
            RuntimeError: If swarm launch fails
        """
    start_time = datetime.now()
    try:
        if not tasks:
            raise ValueError('Cannot launch swarm with empty task list')
        self._validate_swarm_config()
        swarm_state = SwarmState(config=self.config)
        swarm_state.status = 'launching'
        for task in tasks:
            swarm_state.execution_status[task.id] = TaskStatus.PENDING
        distribution_plan = self.distribute_tasks(tasks)
        instances = self._create_instances(distribution_plan)
        swarm_state.instances = {inst.instance_id: inst for inst in instances}
        swarm_state.task_assignments = distribution_plan.instance_assignments
        swarm_state.status = 'active'
        self.active_swarms[swarm_state.swarm_id] = swarm_state
        self.swarm_state = swarm_state
        launch_time = (datetime.now() - start_time).total_seconds()
        self.performance_metrics['swarms_launched'] += 1
        self._update_average_metric('average_swarm_startup_time', launch_time)
        self.add_health_indicator(self.create_health_indicator('swarm_launch', 'healthy', f'Successfully launched swarm {swarm_state.swarm_id} with {len(instances)} instances', {'swarm_id': swarm_state.swarm_id, 'instance_count': len(instances), 'task_count': len(tasks), 'launch_time_seconds': launch_time}))
        self.update_activity()
        logger.info(f'Swarm {swarm_state.swarm_id} launched successfully in {launch_time:.2f}s')
        return swarm_state
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('swarm_launch', 'critical', f'Failed to launch swarm: {str(e)}', {'error': str(e), 'task_count': len(tasks)}))
        logger.error(f'Swarm launch failed: {e}')
        raise RuntimeError(f'Swarm launch failed: {e}') from e
