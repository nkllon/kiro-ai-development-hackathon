from src.rm_ddd.core.health import ModuleHealth

def monitor_swarm(self, swarm_id: Optional[str]=None) -> SwarmState:
    """Get real-time swarm health and progress with systematic monitoring.
        
        Args:
            swarm_id: Specific swarm to monitor, defaults to current swarm
            
        Returns:
            SwarmState: Current swarm status and metrics
        """
    try:
        target_swarm_id = swarm_id or self.swarm_state.swarm_id
        if target_swarm_id not in self.active_swarms:
            raise ValueError(f'Swarm {target_swarm_id} not found')
        swarm = self.active_swarms[target_swarm_id]
        self._update_instance_health(swarm)
        self._update_swarm_metrics(swarm)
        swarm.last_updated = datetime.now()
        self.update_activity()
        return swarm
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('swarm_monitoring', 'warning', f'Failed to monitor swarm: {str(e)}', {'error': str(e), 'swarm_id': swarm_id}))
        logger.warning(f'Swarm monitoring failed: {e}')
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

