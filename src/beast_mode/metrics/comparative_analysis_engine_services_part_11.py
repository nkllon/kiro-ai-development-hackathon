import logging
from src.rm_ddd.core.health import ModuleHealth


    def compare_approaches(self, adhoc_results: List[AdhocSimulationResult], systematic_results: List[SystematicTrackingResult], category: str) -> Optional[ComparisonResult]:
        """
        Perform statistical comparison between ad-hoc and systematic approaches
        
        Args:
            adhoc_results: Results from ad-hoc approach simulation
            systematic_results: Results from systematic approach tracking
            category: Category being compared (decision_making, problem_solving, tool_management)
            
        Returns:
            ComparisonResult with statistical analysis
        """
        self.analysis_count += 1
        try:
            if category == 'decision_making':
                adhoc_values = [r.success_rate for r in adhoc_results]
                systematic_values = [r.success_rate for r in systematic_results]
                metric_name = 'success_rate'
                higher_is_better = True
            elif category == 'problem_solving':
                adhoc_values = [r.time_taken for r in adhoc_results]
                systematic_values = [r.time_taken for r in systematic_results]
                metric_name = 'resolution_time'
                higher_is_better = False
            elif category == 'tool_management':
                adhoc_values = [r.quality_score for r in adhoc_results]
                systematic_values = [r.quality_score for r in systematic_results]
                metric_name = 'quality_score'
                higher_is_better = True
            else:
                self.logger.error(f'Unknown comparison category: {category}')
                return None
            if len(adhoc_values) < self.superiority_thresholds['minimum_sample_size'] or len(systematic_values) < self.superiority_thresholds['minimum_sample_size']:
                self.logger.warning(f'Insufficient samples for {category}: adhoc={len(adhoc_values)}, systematic={len(systematic_values)}')
                return None
            adhoc_mean = statistics.mean(adhoc_values)
            systematic_mean = statistics.mean(systematic_values)
            if higher_is_better:
                improvement_ratio = systematic_mean / adhoc_mean if adhoc_mean > 0 else float('inf')
            else:
                improvement_ratio = adhoc_mean / systematic_mean if systematic_mean > 0 else float('inf')
            adhoc_std = statistics.stdev(adhoc_values) if len(adhoc_values) > 1 else 0
            systematic_std = statistics.stdev(systematic_values) if len(systematic_values) > 1 else 0
            n1, n2 = (len(adhoc_values), len(systematic_values))
            pooled_variance = ((n1 - 1) * adhoc_std ** 2 + (n2 - 1) * systematic_std ** 2) / (n1 + n2 - 2) if n1 + n2 > 2 else 1
            standard_error = math.sqrt(pooled_variance * (1 / n1 + 1 / n2)) if pooled_variance > 0 else 1
            mean_difference = abs(systematic_mean - adhoc_mean)
            t_statistic = mean_difference / standard_error if standard_error > 0 else 0
            margin_of_error = 1.96 * standard_error
            if higher_is_better:
                ci_lower = systematic_mean - adhoc_mean - margin_of_error
                ci_upper = systematic_mean - adhoc_mean + margin_of_error
            else:
                ci_lower = adhoc_mean - systematic_mean - margin_of_error
                ci_upper = adhoc_mean - systematic_mean + margin_of_error
            superiority_proven = improvement_ratio >= self.superiority_thresholds['minimum_improvement_ratio'] and t_statistic >= self.superiority_thresholds['minimum_statistical_significance'] and (ci_lower > 0)
            return ComparisonResult(category=category, adhoc_mean=adhoc_mean, systematic_mean=systematic_mean, improvement_ratio=improvement_ratio, statistical_significance=t_statistic, confidence_interval=(ci_lower, ci_upper), sample_sizes=(len(adhoc_values), len(systematic_values)), superiority_proven=superiority_proven)
        finally:
            self.analysis_count -= 1
            self.total_analyses += 1

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

