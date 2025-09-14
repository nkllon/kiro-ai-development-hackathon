
def _update_instance_health(self, swarm: SwarmState) -> None:
    """Update health status of all instances in swarm."""
    current_time = datetime.now()
    for instance in swarm.instances.values():
        if instance.last_heartbeat:
            time_since_heartbeat = (current_time - instance.last_heartbeat).total_seconds()
            if time_since_heartbeat > self.config.health_check_interval * 2:
                instance.status = 'error'
        instance.performance_metrics['last_health_check'] = current_time.isoformat()
