
def get_all_services_status(self) -> Dict[str, MonitoredService]:
    """Get status of all services"""
    return self.services.copy()
