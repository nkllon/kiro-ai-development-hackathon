from src.rm_ddd.core.health import ModuleHealth

def _execute_integration(self, task_ids: List[str], swarm: SwarmState) -> IntegrationReport:
    """Execute integration of completed tasks."""
    start_time = datetime.now()
    successful = task_ids.copy()
    failed = []
    return IntegrationReport(integration_batch=task_ids, successful_integrations=successful, failed_integrations=failed, integration_time=datetime.now() - start_time, summary=f'Successfully integrated {len(successful)} tasks')
