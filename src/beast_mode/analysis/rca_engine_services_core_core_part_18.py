from src.rm_ddd.core.health import ModuleHealth

def _identify_root_causes(self, failure: Failure, analysis: ComprehensiveAnalysisResult) -> List[RootCause]:
    """Identify root causes from comprehensive analysis including test-specific causes"""
    root_causes = []
    test_analysis = {}
    if hasattr(analysis, 'environmental_factors') and analysis.environmental_factors:
        test_analysis = analysis.environmental_factors.get('test_specific', {})
    is_test_failure = test_analysis.get('is_test_failure', False) or failure.component.startswith('test:') or 'test' in failure.component.lower() or (failure.category in [FailureCategory.PYTEST_FAILURE, FailureCategory.MAKE_TARGET_FAILURE, FailureCategory.INFRASTRUCTURE_FAILURE, FailureCategory.TEST_ENVIRONMENT_FAILURE]) or self._is_pytest_failure(failure) or self._is_make_failure(failure) or self._is_infrastructure_failure(failure)
    if is_test_failure:
        test_root_causes = self._identify_test_specific_root_causes(failure, analysis)
        root_causes.extend(test_root_causes)
    if 'missing_files' in analysis.symptoms:
        if not analysis.tool_health_status.get('makefiles_dir_exists', True):
            root_causes.append(RootCause(cause_type=RootCauseType.MISSING_FILES, description='Missing makefiles/ directory - modular Makefile system not implemented', evidence=['makefiles/ directory does not exist', 'make help fails with include errors'], confidence_score=0.9, impact_severity='high', affected_components=['makefile', 'build_system']))
    if 'permission_denied' in analysis.symptoms:
        root_causes.append(RootCause(cause_type=RootCauseType.PERMISSION_DENIED, description='Insufficient permissions for file access', evidence=['Permission denied error in logs'], confidence_score=0.8, impact_severity='medium', affected_components=[failure.component]))
    if 'missing_dependency' in analysis.symptoms:
        root_causes.append(RootCause(cause_type=RootCauseType.BROKEN_DEPENDENCIES, description='Missing or broken dependencies', evidence=['ImportError in stack trace'], confidence_score=0.7, impact_severity='high', affected_components=[failure.component]))
    return root_causes

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

