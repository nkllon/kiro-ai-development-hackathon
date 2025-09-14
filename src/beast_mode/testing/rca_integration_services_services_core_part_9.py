from src.rm_ddd.core.health import ModuleHealth

def analyze_batch_failures(self, failure_groups: Dict[str, List[TestFailureData]]) -> Dict[str, List[RCAResult]]:
    """
        Batch RCA analysis for processing multiple failures efficiently
        Requirements: 5.1, 5.2, 5.3, 5.4 - Efficient batch processing with correlation analysis
        """
    batch_results = {}
    try:
        for group_name, group_failures in failure_groups.items():
            self.logger.info(f"Processing batch group '{group_name}' with {len(group_failures)} failures")
            rca_failures = [self.convert_to_rca_failure(f) for f in group_failures]
            common_patterns = self._detect_common_failure_patterns(group_failures)
            group_results = []
            shared_context = self._build_shared_analysis_context(group_failures, common_patterns)
            for rca_failure in rca_failures:
                rca_failure.context.update(shared_context)
                result = self.rca_engine.perform_systematic_rca(rca_failure)
                group_results.append(result)
            batch_results[group_name] = group_results
        return batch_results
    except Exception as e:
        self.logger.error(f'Batch failure analysis failed: {e}')
        return {}

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

