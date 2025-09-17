from src.rm_ddd.core.health import ModuleHealth

def detect_failure_correlations(self, failures: List[TestFailureData]) -> Dict[str, Any]:
    """
        Detect correlations and common root causes across multiple failures
        Requirements: 5.1, 5.2, 5.3, 5.4 - Failure correlation detection
        """
    correlations = {'temporal_correlations': [], 'error_pattern_correlations': [], 'dependency_correlations': [], 'environmental_correlations': [], 'common_root_causes': []}
    try:
        correlations['temporal_correlations'] = self._analyze_temporal_correlations(failures)
        correlations['error_pattern_correlations'] = self._analyze_error_pattern_correlations(failures)
        correlations['dependency_correlations'] = self._analyze_dependency_correlations(failures)
        correlations['environmental_correlations'] = self._analyze_environmental_correlations(failures)
        correlations['common_root_causes'] = self._identify_common_root_causes(failures)
        self.logger.info(f"Correlation analysis complete: {len(correlations['common_root_causes'])} common root causes found")
        return correlations
    except Exception as e:
        self.logger.error(f'Failure correlation detection failed: {e}')
        return correlations

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

