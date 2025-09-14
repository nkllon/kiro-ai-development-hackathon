from src.rm_ddd.core.health import ModuleHealth

def _generate_recovery_strategy(self, failure: InstanceFailure, analysis: Dict[str, any]) -> RecoveryPlan:
    """Generate recovery strategy based on failure analysis."""
    if not analysis['recoverable'] or analysis['recovery_complexity'] == 'complex':
        strategy = 'manual'
    elif failure.failure_type == 'timeout':
        strategy = 'restart'
    elif failure.failure_type == 'resource':
        strategy = 'scale_up'
    else:
        strategy = 'reassign'
    return RecoveryPlan(failed_instance=failure.instance_id, recovery_strategy=strategy, estimated_recovery_time=timedelta(minutes=5 if strategy == 'restart' else 15), required_actions=[f'Execute {strategy} recovery for {failure.instance_id}'])
