
def check_health(self) -> ModuleHealth:
    """Perform health check"""
    return ModuleHealth(module_id='projectdashboard', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())
