
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            deployments_available = len(self.deployment_history) > 0
            rdi_compliance = len(self.requirements_traceability) > 0
            optimization_active = len(self.cost_optimization_history) > 0
            health_score = ((1.0 if deployments_available else 0.0) + (1.0 if rdi_compliance else 0.0) + (1.0 if optimization_active else 0.0)) / 3
            issues = []
            if not deployments_available:
                issues.append('No deployment history')
            if not rdi_compliance:
                issues.append('RDI compliance issues')
            if not optimization_active:
                issues.append('No optimization history')
            return ModuleHealth(module_id=self.module_id, status=ModuleStatus.HEALTHY if health_score >= 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={'deployments_completed': len(self.deployment_history), 'rdi_compliance': rdi_compliance, 'cost_optimizations': len(self.cost_optimization_history), 'security_validations': len(self.security_validation_history)}, last_check=datetime.now())
        except Exception as e:
            return ModuleHealth(module_id=self.module_id, status=ModuleStatus.FAILED, health_score=0.0, issues=[f'Health check failed: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())
