
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    GCP Billing Monitor for Beast Mode
    
    Integrates GCP billing data using either:
    1. OpenFlow asset bridge (preferred)
    2. Direct GCP SDK integration (fallback)
    
    Follows Beast Mode's Reflective Module (RM) pattern
    """
