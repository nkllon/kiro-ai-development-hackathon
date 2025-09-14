
def start_monitoring(self):
    """Start the monitoring thread"""
    if self.running:
        self.logger.warning('Monitoring is already running')
        return
    self.running = True
    self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
    self.monitoring_thread.start()
    self.logger.info('Service monitoring started')
