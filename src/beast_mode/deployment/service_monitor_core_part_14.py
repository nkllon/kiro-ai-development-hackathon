from src.rm_ddd.core.health import ModuleHealth

def _trigger_callbacks(self, event: str, service: MonitoredService):
    """Trigger callbacks for an event"""
    for callback in self.callbacks.get(event, []):
        try:
            callback(service)
        except Exception as e:
            self.logger.error(f'Error in callback for {event}: {e}')
