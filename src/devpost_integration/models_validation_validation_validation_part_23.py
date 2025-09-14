
def check_health(self) -> ModuleHealth:
    """Perform health check"""
    try:
        health_score = self._calculate_health_score()
        issues = self._identify_health_issues()
        return ModuleHealth(module_id='submissionrequirement', status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
    except Exception as e:
        self._logger.error(f'Health check failed: {e}')
        return ModuleHealth(module_id='submissionrequirement', status=ModuleStatus.UNHEALTHY, health_score=0.0, issues=[f'Health check error: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

