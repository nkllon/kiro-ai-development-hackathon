from src.rm_ddd.core.health import ModuleHealth

def _get_failure_priority(self, failure: TestFailureData) -> TestFailurePriorityLevel:
    """Get priority level for failure"""
    score = self._calculate_failure_priority_score(failure)
    if score >= 100:
        return TestFailurePriorityLevel.CRITICAL
    elif score >= 50:
        return TestFailurePriorityLevel.HIGH
    elif score >= 20:
        return TestFailurePriorityLevel.MEDIUM
    else:
        return TestFailurePriorityLevel.LOW

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

