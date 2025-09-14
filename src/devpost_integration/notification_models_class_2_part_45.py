
def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.message_id:
        score -= 0.3
    if not self.title:
        score -= 0.2
    if not self.content:
        score -= 0.2
    if not self.recipients:
        score -= 0.2
    return max(0.0, score)
