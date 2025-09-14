
def get_service_status(self, service_name: str) -> Optional[MonitoredService]:
    """Get status of a specific service"""
    return self.services.get(service_name)
