
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
