
def _monitoring_loop(self):
    """Main monitoring loop"""
    while self.running:
        try:
            for service_name, service in self.services.items():
                self._check_service_health(service)
                self._update_service_metrics(service)
            time.sleep(self.config.monitoring.health_check_interval)
        except Exception as e:
            self.logger.error(f'Error in monitoring loop: {e}')
            time.sleep(5)
