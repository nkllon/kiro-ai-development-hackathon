
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            agents_available = len(self.agents) > 0
            rdi_compliance = len(self.requirements_traceability) > 0
            collaboration_active = len(self.collaboration_history) > 0
            health_score = ((1.0 if agents_available else 0.0) + (1.0 if rdi_compliance else 0.0) + (1.0 if collaboration_active else 0.0)) / 3
            issues = []
            if not agents_available:
                issues.append('No agents available')
            if not rdi_compliance:
                issues.append('RDI compliance issues')
            if not collaboration_active:
                issues.append('No collaboration history')
            return ModuleHealth(module_id=self.module_id, status=ModuleStatus.HEALTHY if health_score >= 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={'agents_available': len(self.agents), 'rdi_compliance': rdi_compliance, 'collaborations_completed': len(self.collaboration_history), 'conflicts_resolved': len(self.conflict_resolution_history)}, last_check=datetime.now())
        except Exception as e:
            return ModuleHealth(module_id=self.module_id, status=ModuleStatus.FAILED, health_score=0.0, issues=[f'Health check failed: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

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

