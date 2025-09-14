from src.rm_ddd.core.health import ModuleHealth

def _validate_service_health(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Service health validation"""
    results = []
    expected_processes = ['redis-server', 'python']
    for process_name in expected_processes:
        result = self._check_process_running(process_name)
        results.append(result)
    log_files = [config.agent.mailbox_log_file]
    for log_file in log_files:
        result = self._check_log_file_health(log_file)
        results.append(result)
    return results
