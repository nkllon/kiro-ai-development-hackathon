
def stop_monitoring(self):
    """Stop the monitoring thread"""
    if not self.running:
        return
    self.running = False
    if self.monitoring_thread:
        self.monitoring_thread.join(timeout=5)
    self.logger.info('Service monitoring stopped')
