
def check_health(self) -> ModuleHealth:
    """Perform health check"""
    try:
        health_score = self._calculate_health_score()
        issues = self._identify_health_issues()
        return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
    except Exception as e:
        self._logger.error(f'Health check failed: {e}')
        return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.UNHEALTHY, health_score=0.0, issues=[f'Health check error: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
