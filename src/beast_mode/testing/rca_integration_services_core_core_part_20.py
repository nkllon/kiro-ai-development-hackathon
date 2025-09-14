
def _calculate_correlation_priority_score(self, failure: TestFailureData, all_failures: List[TestFailureData]) -> float:
    """Calculate priority score based on correlation with other failures"""
    correlation_score = 0.0
    similar_failures = 0
    for other_failure in all_failures:
        if other_failure != failure:
            similarity = self._calculate_failure_similarity(failure, other_failure)
            if similarity > 0.5:
                similar_failures += 1
    correlation_score = min(similar_failures * 10.0, 50.0)
    return correlation_score
