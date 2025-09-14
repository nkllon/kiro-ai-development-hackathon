
def _analyze_infrastructure_failures(self, failure: Failure) -> Dict[str, Any]:
    """Analyze infrastructure-specific failures - Requirement 5.3"""
    infrastructure_analysis = {}
    try:
        if self._is_infrastructure_failure(failure):
            infrastructure_analysis['system_config'] = self._analyze_system_configuration(failure)
            infrastructure_analysis['permissions'] = self._analyze_permissions(failure)
            infrastructure_analysis['environment'] = self._analyze_infrastructure_environment(failure)
            infrastructure_analysis['resources'] = self._analyze_resource_availability(failure)
            infrastructure_analysis['analysis_confidence'] = 0.7
        else:
            infrastructure_analysis['applicable'] = False
            infrastructure_analysis['reason'] = 'Not an infrastructure failure'
    except Exception as e:
        infrastructure_analysis['analysis_error'] = str(e)
    return infrastructure_analysis
