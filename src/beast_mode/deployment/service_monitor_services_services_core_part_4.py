
def start_service(self, service_name: str) -> bool:
    """Start a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.status == ServiceStatus.RUNNING:
        self.logger.warning(f'Service {service_name} is already running')
        return True
    try:
        service.status = ServiceStatus.STARTING
        self.logger.info(f'Starting service: {service_name}')
        env = service.environment.copy()
        process = subprocess.Popen(service.command, cwd=service.working_directory, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else lambda: None)
        service.process = process
        service.pid = process.pid
        service.status = ServiceStatus.RUNNING
        service.started_at = time.time()
        service.metrics.restart_count += 1
        service.metrics.last_restart = time.strftime('%Y-%m-%d %H:%M:%S')
        self.logger.info(f'Service {service_name} started with PID {service.pid}')
        self._trigger_callbacks('service_started', service)
        return True
    except Exception as e:
        service.status = ServiceStatus.FAILED
        self.logger.error(f'Failed to start service {service_name}: {e}')
        self._trigger_callbacks('service_failed', service)
        return False
