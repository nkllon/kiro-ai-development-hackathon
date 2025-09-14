
def __init__(self, pattern_library_path: Optional[str]=None):
    super().__init__('rca_engine')
    self.pattern_library_path = pattern_library_path or 'patterns/rca_patterns.json'
    self.pattern_library: Dict[str, PreventionPattern] = {}
    self.pattern_index: Dict[str, List[str]] = {}
    self.rca_count = 0
    self.successful_fixes = 0
    self.pattern_matches = 0
    self.total_analysis_time = 0.0
    self._load_pattern_library()
    self.analysis_components = {'symptoms': self._analyze_symptoms, 'tool_health': self._analyze_tool_health, 'dependencies': self._analyze_dependencies, 'configuration': self._analyze_configuration, 'installation': self._analyze_installation_integrity, 'environment': self._analyze_environmental_factors, 'test_specific': self._analyze_test_specific_factors, 'pytest_analysis': self._analyze_pytest_failures, 'makefile_analysis': self._analyze_makefile_failures, 'infrastructure_analysis': self._analyze_infrastructure_failures}
    self._update_health_indicator('rca_engine_readiness', HealthStatus.HEALTHY, f'ready_with_{len(self.pattern_library)}_patterns', 'RCA engine ready for systematic failure analysis')
