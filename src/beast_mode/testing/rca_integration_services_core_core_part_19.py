
def _calculate_failure_urgency_score(self, failure: TestFailureData) -> float:
    """Calculate urgency score based on timing and context"""
    urgency_score = 0.0
    time_since_failure = (datetime.now() - failure.failure_timestamp).total_seconds()
    if time_since_failure < 300:
        urgency_score += 30.0
    elif time_since_failure < 1800:
        urgency_score += 20.0
    elif time_since_failure < 3600:
        urgency_score += 10.0
    if failure.test_context.get('environment_variables', {}).get('CI'):
        urgency_score += 25.0
    return urgency_score
