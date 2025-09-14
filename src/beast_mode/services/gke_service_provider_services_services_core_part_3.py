from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for GKE service provider"""
    dependencies_healthy = self.pdca_orchestrator.is_healthy() and self.registry_engine.is_healthy() and self.makefile_manager.is_healthy()
    available_services = sum((1 for service in self.service_registry.values() if service['status'] == ServiceStatus.AVAILABLE))
    services_healthy = available_services >= 3
    total_load = sum((service['current_load'] for service in self.service_registry.values()))
    total_capacity = sum((service['max_concurrent'] for service in self.service_registry.values()))
    capacity_healthy = total_load < total_capacity * 0.9
    return dependencies_healthy and services_healthy and capacity_healthy and (not self._degradation_active)
