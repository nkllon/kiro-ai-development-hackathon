
def __init__(self, config: SwarmConfig):
    super().__init__('OrchestrationController', '1.0.0')
    self.config = config
    self.swarm_state = SwarmState(config=config)
    self.active_swarms: Dict[str, SwarmState] = {}
    self.task_queue: List[Task] = []
    self.distribution_history: List[DistributionPlan] = []
    self.recovery_history: List[RecoveryPlan] = []
    self.performance_metrics = {'swarms_launched': 0, 'tasks_distributed': 0, 'successful_integrations': 0, 'failed_recoveries': 0, 'average_swarm_startup_time': 0.0, 'average_task_completion_time': 0.0}
    logger.info(f'OrchestrationController initialized with config: {config.model_dump()}')
