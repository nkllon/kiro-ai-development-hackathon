
def is_healthy(self) -> bool:
    """Health assessment for GKE service consumer"""
    core_services_healthy = all((status != ServiceStatus.UNAVAILABLE for status in self.service_status.values()))
    components_healthy = self.pdca_orchestrator.is_healthy() and self.registry_intelligence.is_healthy() and self.makefile_health_manager.is_healthy() and self.test_suite.is_healthy()
    return core_services_healthy and components_healthy and (not self._degradation_active)
