from src.rm_ddd.core.health import ModuleHealth

def prioritize_failures(self, failures: List[TestFailureData]) -> List[TestFailureData]:
    """
        Advanced prioritization system for analyzing most critical failures first
        Requirements: 1.3, 5.1, 5.2, 5.3, 5.4 - Multi-dimensional failure prioritization
        """
    try:
        scored_failures = []
        for failure in failures:
            base_score = self._calculate_failure_priority_score(failure)
            impact_score = self._calculate_failure_impact_score(failure)
            urgency_score = self._calculate_failure_urgency_score(failure)
            correlation_score = self._calculate_correlation_priority_score(failure, failures)
            total_score = base_score * 0.4 + impact_score * 0.3 + urgency_score * 0.2 + correlation_score * 0.1
            scored_failures.append((failure, total_score))
        prioritized = [failure for failure, score in sorted(scored_failures, key=lambda x: x[1], reverse=True)]
        prioritized = self._apply_critical_priority_boosting(prioritized)
        priority_info = [(f.test_name, self._get_failure_priority(f).value, scored_failures[i][1]) for i, f in enumerate(prioritized[:5])]
        self.logger.info(f'Top 5 prioritized failures: {priority_info}')
        return prioritized
    except Exception as e:
        self.logger.error(f'Advanced failure prioritization failed: {e}')
        return failures
