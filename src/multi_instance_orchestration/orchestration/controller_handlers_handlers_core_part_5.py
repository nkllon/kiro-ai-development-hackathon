from src.rm_ddd.core.health import ModuleHealth

def handle_failure(self, failure: InstanceFailure) -> RecoveryPlan:
    """Generate systematic recovery plan for failed instances.
        
        Args:
            failure: Instance failure information
            
        Returns:
            RecoveryPlan: Systematic recovery strategy
        """
    start_time = datetime.now()
    try:
        failure_analysis = self._analyze_failure(failure)
        recovery_plan = self._generate_recovery_strategy(failure, failure_analysis)
        self.recovery_history.append(recovery_plan)
        if not recovery_plan.recovery_strategy == 'manual':
            recovery_success = self._execute_recovery_plan(recovery_plan)
            if not recovery_success:
                self.performance_metrics['failed_recoveries'] += 1
        self.add_health_indicator(self.create_health_indicator('failure_recovery', 'warning' if recovery_plan.recovery_strategy != 'manual' else 'critical', f'Generated recovery plan for instance {failure.instance_id}', {'instance_id': failure.instance_id, 'failure_type': failure.failure_type, 'recovery_strategy': recovery_plan.recovery_strategy, 'affected_tasks': len(failure.affected_tasks)}))
        self.update_activity()
        logger.info(f'Recovery plan generated for {failure.instance_id}: {recovery_plan.recovery_strategy}')
        return recovery_plan
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('failure_recovery', 'critical', f'Failed to generate recovery plan: {str(e)}', {'error': str(e), 'instance_id': failure.instance_id}))
        logger.error(f'Recovery plan generation failed: {e}')
        raise

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

