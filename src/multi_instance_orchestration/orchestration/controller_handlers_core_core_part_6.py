
def integrate_results(self, swarm_id: Optional[str]=None) -> IntegrationReport:
    """Systematically integrate completed work with quality gates.
        
        Args:
            swarm_id: Specific swarm to integrate, defaults to current swarm
            
        Returns:
            IntegrationReport: Integration results and status
        """
    start_time = datetime.now()
    try:
        target_swarm_id = swarm_id or self.swarm_state.swarm_id
        swarm = self.active_swarms[target_swarm_id]
        completed_tasks = self._get_completed_tasks(swarm)
        if not completed_tasks:
            return IntegrationReport(integration_time=datetime.now() - start_time, summary='No completed tasks ready for integration')
        integration_report = self._execute_integration(completed_tasks, swarm)
        self.performance_metrics['successful_integrations'] += len(integration_report.successful_integrations)
        self.add_health_indicator(self.create_health_indicator('integration', 'healthy' if not integration_report.failed_integrations else 'warning', f'Integrated {len(integration_report.successful_integrations)} tasks, {len(integration_report.failed_integrations)} failed', {'successful': len(integration_report.successful_integrations), 'failed': len(integration_report.failed_integrations), 'conflicts': len(integration_report.conflicts_remaining)}))
        self.update_activity()
        logger.info(f'Integration completed: {integration_report.summary}')
        return integration_report
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('integration', 'critical', f'Integration failed: {str(e)}', {'error': str(e), 'swarm_id': swarm_id}))
        logger.error(f'Integration failed: {e}')
        raise
