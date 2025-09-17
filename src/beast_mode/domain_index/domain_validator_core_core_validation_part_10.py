from src.rm_ddd.core.health import ModuleHealth

    def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        return self.validate_dependencies(domains)
    self._consistency_checks.append(ConsistencyCheck(name='dependency_consistency', description='Check domain dependency consistency', severity=IssueSeverity.CRITICAL, checker_func=check_dependency_consistency))

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

